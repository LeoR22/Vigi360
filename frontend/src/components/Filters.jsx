import { useEffect, useState } from 'react';
import { Card } from './ui/card';
import { TrendingUp, MapPin, Target, ChevronLeft, ChevronRight } from 'lucide-react';
import { getPredictionTrend, getMunicipiosDistribution } from '../services/analytics';
import './Filters.css';

export function PredictiveAnalytics({ predictionData, municipalityData, incidentTypeData }) {
  const [localPredictionData, setLocalPredictionData] = useState(predictionData || null);
  const [localMunicipalityData, setLocalMunicipalityData] = useState(municipalityData || []);
  const [isLoadingPrediction, setIsLoadingPrediction] = useState(false);
  const [isLoadingMunicipality, setIsLoadingMunicipality] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 12;

  useEffect(() => {
    // Fetch prediction data from /risk/predict endpoint
    if (!predictionData) {
      setIsLoadingPrediction(true);
      // Asumiendo que tienes una función para obtener la predicción de riesgo
      // Si no la tienes, agrégala a tu archivo de servicios
      fetch('http://localhost:8000/analytics/risk/predict') // Ajusta la URL según tu configuración
        .then(response => response.json())
        .then((data) => {
          console.log('Datos de predicción recibidos:', data);
          setLocalPredictionData(data);
        })
        .catch((err) => {
          console.error('Error fetching risk prediction:', err);
          setLocalPredictionData(null);
        })
        .finally(() => setIsLoadingPrediction(false));
    }
  }, [predictionData]);

  useEffect(() => {
    // Fetch municipality distribution if not provided
    if (!municipalityData || municipalityData.length === 0) {
      setIsLoadingMunicipality(true);
      getMunicipiosDistribution()
        .then((data) => {
          const transformed = Array.isArray(data) ? data.map(item => ({
            name: item.municipio,
            incidents: item.incidentes || 0,
          })) : [];
          setLocalMunicipalityData(transformed);
        })
        .catch((err) => {
          console.error('Error fetching municipios distribution:', err);
          setLocalMunicipalityData([]);
        })
        .finally(() => setIsLoadingMunicipality(false));
    }
  }, [municipalityData]);

  // Cálculos para paginación
  const totalPages = Math.ceil(localMunicipalityData.length / itemsPerPage);
  const startIndex = currentPage * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentMunicipalities = localMunicipalityData.slice(startIndex, endIndex);

  const handlePrevPage = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1));
  };

  const handleNextPage = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1));
  };

  return (
    <div className="analytics-grid">
      {/* Predictive Analysis Chart */}
<Card style={{
  backgroundColor: 'white',
  borderRadius: '12px',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  overflow: 'hidden'
}}>
  {/* Cabecera */}
  <div style={{
    background: 'linear-gradient(to right, #2563eb, #1d4ed8)',
    padding: '1rem 1.5rem',
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  }}>
    <div style={{
      backgroundColor: 'rgba(255, 255, 255, 0.2)',
      padding: '8px',
      borderRadius: '8px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <TrendingUp style={{ height: '20px', width: '20px', color: 'white' }} />
    </div>
    <div>
      <h2 style={{
        color: 'white',
        fontSize: '16px',
        fontWeight: '600',
        margin: '0'
      }}>Proyección de Riesgos</h2>
      <p style={{
        color: '#bfdbfe',
        fontSize: '12px',
        margin: '0'
      }}>Escenarios futuros y patrones críticos</p>
    </div>
  </div>

  {/* Contenido */}
  <div style={{ padding: '1.5rem' }}>
    {/* Estado de carga */}
    {isLoadingPrediction && (
      <div style={{ textAlign: 'center', padding: '1rem' }}>
        <div style={{
          display: 'inline-block',
          animation: 'spin 1s linear infinite',
          borderRadius: '50%',
          height: '32px',
          width: '32px',
          borderBottom: '2px solid #2563eb',
          marginBottom: '8px'
        }} />
        <p style={{ fontSize: '14px', color: '#6b7280' }}>Cargando datos de predicción...</p>
      </div>
    )}

    {/* Estado sin datos */}
    {!isLoadingPrediction && !localPredictionData && (
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#fef3c7',
        borderRadius: '8px',
        borderLeft: '4px solid #f59e0b'
      }}>
        <p style={{ fontSize: '14px', color: '#92400e', margin: 0 }}>⚠️ No hay datos de predicción disponibles</p>
        <p style={{ fontSize: '12px', color: '#b45309', marginTop: '4px' }}>Verifica la conexión con el servidor</p>
      </div>
    )}

    {/* Probabilidad General */}
    {localPredictionData?.probability !== undefined && (
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#eff6ff',
        borderRadius: '8px',
        borderLeft: '4px solid #2563eb'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '14px', fontWeight: '600', color: '#1e40af' }}>
            Probabilidad General de Incidentes
          </span>
          <span style={{ fontSize: '24px', fontWeight: '700', color: '#2563eb' }}>
            {(localPredictionData.probability * 100).toFixed(2)}%
          </span>
        </div>
        {localPredictionData.anio && localPredictionData.mes && (
          <p style={{ fontSize: '12px', color: '#2563eb', marginTop: '6px' }}>
            Predicción para: {localPredictionData.mes}/{localPredictionData.anio}
          </p>
        )}
      </div>
    )}

    {/* Contexto Narrativo */}
    {localPredictionData?.contexto && (
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#ede9fe',
        borderRadius: '8px',
        borderLeft: '4px solid #7c3aed'
      }}>
        <h4 style={{ fontSize: '14px', fontWeight: '600', color: '#5b21b6', marginBottom: '8px' }}>
          Análisis Contextual
        </h4>
        <p style={{ fontSize: '14px', color: '#6d28d9', marginBottom: '12px' }}>
          {localPredictionData.contexto.mensaje}
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', fontSize: '12px' }}>
          {[
            { label: 'Género', value: localPredictionData.contexto.genero_predominante },
            { label: 'Grupo Etario', value: localPredictionData.contexto.grupo_etario_predominante },
            { label: 'Día Crítico', value: localPredictionData.contexto.dia_semana_critico },
            { label: 'Franja Horaria', value: localPredictionData.contexto.franja_horaria_critica },
            { label: 'Tipo de Delito', value: localPredictionData.contexto.tipo_delito_predominante, full: true }
          ].map((item, idx) => (
            <div key={idx} style={{
              backgroundColor: 'rgba(255,255,255,0.6)',
              padding: '8px',
              borderRadius: '6px',
              gridColumn: item.full ? 'span 2' : 'auto'
            }}>
              <strong style={{ color: '#5b21b6' }}>{item.label}:</strong>
              <p style={{ color: '#6d28d9', margin: 0 }}>{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    )}
    {/* Ranking de Municipios */}
{(() => {
  const ranking = localPredictionData?.ranking_municipios || localPredictionData?.ranking || [];

  const getChipStyle = (p) => {
    if (p > 0.7) return { backgroundColor: '#fee2e2', color: '#b91c1c' };      // rojo suave
    if (p > 0.4) return { backgroundColor: '#fef9c3', color: '#a16207' };      // amarillo suave
    return { backgroundColor: '#dcfce7', color: '#166534' };                    // verde suave
  };

  if (!ranking || ranking.length === 0) {
    return (
      <div style={{
        marginTop: '1rem',
        padding: '1rem',
        backgroundColor: '#f9fafb',
        borderRadius: '12px',
        border: '1px solid #e5e7eb',
        textAlign: 'center'
      }}>
        <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>No hay ranking de municipios disponible</p>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: 'white',
      borderRadius: '12px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      border: '1px solid #e5e7eb',
      overflow: 'hidden'
    }}>
      {/* Cabecera del bloque */}
      <div style={{
        background: 'linear-gradient(to right, #2563eb, #1d4ed8)',
        padding: '0.75rem 1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <div style={{
          backgroundColor: 'rgba(255,255,255,0.2)',
          padding: '6px',
          borderRadius: '8px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{ fontSize: '16px', color: 'white' }}>🏆</span>
        </div>
        <div>
          <h4 style={{ margin: 0, color: 'white', fontSize: '14px', fontWeight: 700 }}>
            Top 5 Municipios Críticos
          </h4>

          <p style={{ margin: 0, color: '#bfdbfe', fontSize: '12px' }}>
            Probabilidad estimada por municipio
          </p>
        </div>
      </div>

      {/* Tabla */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
              <th style={{ textAlign: 'left', padding: '10px', fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>
                Ranking
              </th>
              <th style={{ textAlign: 'left', padding: '10px', fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>
                Municipio
              </th>
              <th style={{ textAlign: 'right', padding: '10px', fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>
                Probabilidad
              </th>
              <th style={{ textAlign: 'right', padding: '10px', fontSize: '12px', color: '#6b7280', fontWeight: 600 }}>
                Intensidad
              </th>
            </tr>
          </thead>
          <tbody>
            {ranking.slice(0, 5).map((item, idx) => {
              const p = item.probabilidad ?? item.probability ?? 0;
              const chipStyle = getChipStyle(p);
              const medalStyle =
                idx === 0 ? { backgroundColor: '#facc15', color: '#78350f' } :
                idx === 1 ? { backgroundColor: '#e5e7eb', color: '#374151' } :
                idx === 2 ? { backgroundColor: '#fdba74', color: '#7c2d12' } :
                             { backgroundColor: '#f3f4f6', color: '#6b7280' };

              return (
                <tr
                  key={idx}
                  style={{
                    borderBottom: '1px solid #f1f5f9',
                    transition: 'background-color 150ms ease',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'}
                  onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                >
                  <td style={{ padding: '12px 10px' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '24px',
                      height: '24px',
                      borderRadius: '999px',
                      fontSize: '11px',
                      fontWeight: 700,
                      ...medalStyle
                    }}>
                      {idx + 1}
                    </span>
                  </td>
                  <td style={{ padding: '12px 10px', color: '#111827', fontWeight: 500, fontSize: '13px' }}>
                    {item.municipio}
                  </td>
                  <td style={{ padding: '12px 10px', textAlign: 'right' }}>
                    <span style={{
                      display: 'inline-block',
                      padding: '4px 10px',
                      borderRadius: '999px',
                      fontSize: '12px',
                      fontWeight: 600,
                      ...chipStyle
                    }}>
                      {(p * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td style={{ padding: '12px 10px', textAlign: 'right', minWidth: '140px' }}>
                    {/* Barra de intensidad visual */}
                    <div style={{
                      backgroundColor: '#e5e7eb',
                      borderRadius: '999px',
                      height: '8px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${Math.round(p * 100)}%`,
                        height: '100%',
                        background: p > 0.7
                          ? 'linear-gradient(to right, #ef4444, #dc2626)'
                          : p > 0.4
                          ? 'linear-gradient(to right, #f59e0b, #d97706)'
                          : 'linear-gradient(to right, #22c55e, #16a34a)',
                        transition: 'width 300ms ease'
                      }} />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
})()}

  </div>

</Card>
      
      {/* Municipality Distribution */}
      <Card className="analytics-card">
        <div className="analytics-header municipality-header">
          <div className="header-icon-wrapper">
            <MapPin />
          </div>
          <div className="header-text-content">
            <h3>Distribución por Municipio</h3>
            <p>Incidentes por área metropolitana</p>
          </div>
        </div>
        <div className="analytics-content">
          <div className="municipality-list">
            {isLoadingMunicipality ? (
              <div className="placeholder">Cargando datos...</div>
            ) : currentMunicipalities.length > 0 ? (
              currentMunicipalities.map((item, index) => {
                const maxIncidents = Math.max(...localMunicipalityData.map(m => m.incidents), 1);
                return (
                  <div key={index} className="municipality-item">
                    <span className="municipality-name">{item.name}</span>
                    <div className="municipality-bar">
                      <div 
                        className="bar-fill"
                        style={{ width: `${(item.incidents / maxIncidents * 100)}%` }}
                      ></div>
                    </div>
                    <span className="municipality-count">{item.incidents}</span>
                  </div>
                );
              })
            ) : (
              <div className="placeholder">No hay datos disponibles</div>
            )}
          </div>
          
          {/* Controles de paginación */}
          {localMunicipalityData.length > itemsPerPage && (
            <div className="flex items-center justify-center gap-4 mt-4 px-2">
              <button
                onClick={handlePrevPage}
                disabled={currentPage === 0}
                className="flex items-center gap-1 px-3 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={16} />
                <span className="text-sm">Anterior</span>
              </button>
              
              <span className="text-sm text-gray-600">
                Página {currentPage + 1} de {totalPages}
              </span>
              
              <button
                onClick={handleNextPage}
                disabled={currentPage === totalPages - 1}
                className="flex items-center gap-1 px-3 py-2 rounded-lg border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span className="text-sm">Siguiente</span>
                <ChevronRight size={16} />
              </button>
            </div>
          )}
        </div>
      </Card>

      {/* Incident Type Distribution */}
      {incidentTypeData && incidentTypeData.length > 0 && (
        <Card className="analytics-card full-width">
          <div className="analytics-header incidents-header">
            <div className="header-icon-wrapper">
              <Target />
            </div>
            <div className="header-text-content">
              <h3>Tipos de Incidentes</h3>
              <p>Distribución por categoría</p>
            </div>
          </div>
          <div className="analytics-content">
            <div className="incidents-grid">
              {incidentTypeData.map((item, index) => (
                <div key={index} className="incident-type-card">
                  <div className="incident-color" style={{ backgroundColor: item.color }}></div>
                  <div className="incident-info">
                    <p className="incident-name">{item.name}</p>
                    <p className="incident-count">{item.value} casos</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}