"""Pipeline reproducible StreamView EP5. Fuentes originales inmutables; exportación única para Looker."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
OUT = ROOT / 'data' / 'processed' / 'looker' /'catalogo_looker_ep5.csv'
SOURCES = ('netflix_movies_detailed_up_to_2025.csv', 'netflix_tv_shows_detailed_up_to_2025.csv')
# Armonización conservadora de géneros; no fusionamos categorías que no sean semánticamente equivalentes.
GENRE_MAP = {'Action & Adventure':'Acción y aventura', 'Action':'Acción', 'Adventure':'Aventura',
             'Sci-Fi & Fantasy':'Ciencia ficción y fantasía', 'Science Fiction':'Ciencia ficción',
             'Fantasy':'Fantasía', 'War & Politics':'Guerra y política', 'War':'Guerra',
             'Unknown':None}
LANG = {'en':'Inglés','zh':'Chino','cn':'Chino','ja':'Japonés','ko':'Coreano','es':'Español',
        'fr':'Francés','de':'Alemán','hi':'Hindi','tl':'Filipino/Tagalo','pt':'Portugués',
        'ru':'Ruso','it':'Italiano','tr':'Turco','ar':'Árabe'}

def load_sources():
    parts = [pd.read_csv(RAW / p, low_memory=False) for p in SOURCES]
    for part, typ in zip(parts, ('Movie','TV Show')):
        assert (part['type'] == typ).all(), f'Tipo inválido en {typ}'
    return pd.concat(parts, ignore_index=True, sort=False)

def audit(df):
    return pd.DataFrame({'campo':df.columns,'faltantes':df.isna().sum().values,
                         'porcentaje':(df.isna().mean().values*100).round(2)})

def _split(text):
    if pd.isna(text) or not str(text).strip(): return []
    return [s.strip() for s in str(text).split(',') if s.strip()]

def _clean_genres(value):
    result = []
    for s in _split(value):
        s=GENRE_MAP.get(s,s)
        if s and s not in result: result.append(s)
    return result

def clean(raw):
    """Una fila por contenido; conservar nulos estructurales; resolver 9 conflictos de IDs."""
    df=raw.copy()
    # Identificadores repetidos del mismo título, año y tipo: conservar registro con más votos;
    # en empate, mayor popularidad. NO se interpreta como evolución de popularidad.
    df['show_id']=df['show_id'].astype('string').str.strip()
    df['title']=df['title'].astype('string').str.strip()
    df['_row']=np.arange(len(df))
    df['vote_count']=pd.to_numeric(df['vote_count'], errors='coerce')
    df['popularity']=pd.to_numeric(df['popularity'], errors='coerce')
    df=df.sort_values(['type','show_id','vote_count','popularity','_row'],
                      ascending=[True,True,False,False,True],kind='stable')
    df=df.drop_duplicates(['type','show_id'],keep='first').sort_values('_row').drop(columns='_row').reset_index(drop=True)
    assert not df.duplicated(['type','show_id']).any()
    df['content_key']=df['type'].map({'Movie':'M','TV Show':'S'})+'_'+df['show_id'].astype(str)
    assert df['content_key'].is_unique
    df['release_year']=pd.to_numeric(df['release_year'],errors='coerce').astype('Int64')
    df['date_added']=pd.to_datetime(df['date_added'],errors='coerce')
    df['vote_average']=pd.to_numeric(df['vote_average'],errors='coerce')
    df['vote_count']=df['vote_count'].fillna(0).astype(int)
    # No reemplazar votaciones inexistentes por cero; 50 votos para comparación robusta.
    df['nota_con_votos']=df['vote_average'].where((df['vote_count']>=1)&df['vote_average'].between(0,10))
    df['nota_confiable_50']=df['vote_average'].where((df['vote_count']>=50)&df['vote_average'].between(0,10))
    df['tiene_50_votos']=(df['vote_count']>=50).astype(int)
    # Popularidad relativa: no sumar ni promediar películas y series como indicador comparativo.
    df['popularidad_percentil_tipo']=df.groupby('type')['popularity'].rank(pct=True)*100
    df['generos_lista']=df['genres'].map(_clean_genres)
    df['genero_principal']=df['generos_lista'].map(lambda x:x[0] if x else pd.NA)
    df['generos_armonizados']=df['generos_lista'].map(lambda x:' | '.join(x) if x else pd.NA)
    df['cantidad_generos']=df['generos_lista'].map(len)
    df['pais_principal']=df['country'].map(lambda v:_split(v)[0] if _split(v) else pd.NA)
    df['director_principal']=df['director'].map(lambda v:_split(v)[0] if _split(v) else pd.NA)
    df['idioma_codigo']=df['language'].astype('string').str.strip().str.lower()
    df['idioma_nombre']=df['idioma_codigo'].map(LANG).fillna(df['idioma_codigo'])
    df['temporadas']=pd.to_numeric(df['duration'].astype('string').str.extract(r'(\d+)',expand=False),errors='coerce').where(df['type']=='TV Show')
    for c in ['budget','revenue']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df['finanzas_validas']=(df['type'].eq('Movie') & df['budget'].ge(10000) & df['revenue'].ge(10000))
    df['presupuesto_usd']=df['budget'].where(df['finanzas_validas'])
    df['ingresos_usd']=df['revenue'].where(df['finanzas_validas'])
    df['multiplo_ingresos']=df['ingresos_usd']/df['presupuesto_usd']
    df['roi_neto']=df['multiplo_ingresos']-1
    df['ganancia_usd']=df['ingresos_usd']-df['presupuesto_usd']
    df['recupera_presupuesto']=df['multiplo_ingresos'].ge(1).where(df['finanzas_validas'])
    df['rango_presupuesto']=pd.cut(df['presupuesto_usd'],bins=[0,1e6,1e7,5e7,1e8,np.inf],
        labels=['< 1 M','1–10 M','10–50 M','50–100 M','> 100 M'],right=False)
    # El catálogo tiene selección 1000/1000 por año; no inferir crecimiento a partir de eso.
    df['anio_estreno']=df['release_year']
    return df

def looker_table(df):
    """Exporta UNA tabla de grano título; los multi-géneros completos quedan como texto informativo.
    Para clasificaciones consistentes, los gráficos/filtros por género usan SOLO genero_principal.
    """
    cols=['content_key','type','title','anio_estreno','date_added','genero_principal',
          'generos_armonizados','cantidad_generos','pais_principal','idioma_codigo',
          'idioma_nombre','director_principal','temporadas','popularity',
          'popularidad_percentil_tipo','vote_count','nota_con_votos','nota_confiable_50',
          'tiene_50_votos','finanzas_validas','presupuesto_usd','ingresos_usd',
          'multiplo_ingresos','roi_neto','ganancia_usd','recupera_presupuesto','rango_presupuesto']
    return df[cols].copy()

def kpis(df):
    financial=df[df['finanzas_validas']]
    reliable=df[df['nota_confiable_50'].notna()]
    return {'titulos_unicos':len(df),'peliculas':int(df.type.eq('Movie').sum()),
            'series':int(df.type.eq('TV Show').sum()),
            'n_con_50_votos':len(reliable),'nota_media_50_votos':round(reliable.nota_confiable_50.mean(),3),
            'popularidad_media_total_solo_control':round(df.popularity.mean(),3),
            'peliculas_financieras':len(financial),
            'multiplo_ingresos_agregado':round(financial.ingresos_usd.sum()/financial.presupuesto_usd.sum(),4),
            'multiplo_ingresos_mediano':round(financial.multiplo_ingresos.median(),4),
            'pct_recupera_presupuesto':round(financial.recupera_presupuesto.mean()*100,2),
            'ganancia_media_usd':round(financial.ganancia_usd.mean(),2)}

def export():
    df=clean(load_sources())
    table=looker_table(df)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    table.to_csv(OUT,index=False,encoding='utf-8-sig',float_format='%.6f',date_format='%Y-%m-%d')
    assert pd.read_csv(OUT).shape[0]==len(df)
    return df,table
