import React, { useState, useEffect, useMemo } from 'react';
import { initializeApp } from 'firebase/app';
import {
  getFirestore, collection, query, onSnapshot,
  doc, setDoc, updateDoc, addDoc, where, getDocs
} from 'firebase/firestore';
import {
  getAuth, signInAnonymously, onAuthStateChanged
} from 'firebase/auth';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import {
  Users, BookOpen, AlertTriangle, Activity,
  Search, Plus, Copy, LogOut, CheckCircle, XCircle,
  ShieldAlert, Clock, Award
} from 'lucide-react';

// --- CONFIGURACIÓN FIREBASE ---
const firebaseConfig = JSON.parse(__firebase_config || '{}');
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-logicbot';

// --- CONSTANTES ---
const TEMAS_JAVA = [
  "Variables y Primitivos",
  "Operadores Lógicos",
  "Condicionales (if-else)",
  "Ciclos (for, while)",
  "Arrays (Arreglos)",
  "Métodos y Funciones",
  "Clases y Objetos (OOP)"
];

const COLORS = {
  success: '#10B981', // Green
  warning: '#F59E0B', // Yellow
  danger: '#EF4444',  // Red
  primary: '#3B82F6', // Blue
  dark: '#1F2937'     // Gray-900
};

// --- COMPONENTES AUXILIARES ---

const Card = ({ children, className = "" }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-100 p-6 ${className}`}>
    {children}
  </div>
);

const Badge = ({ type, text }) => {
  const styles = {
    success: "bg-green-100 text-green-800",
    warning: "bg-yellow-100 text-yellow-800",
    danger: "bg-red-100 text-red-800",
    neutral: "bg-gray-100 text-gray-800",
    primary: "bg-blue-100 text-blue-800"
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[type] || styles.neutral}`}>
      {text}
    </span>
  );
};

// --- COMPONENTE PRINCIPAL ---

export default function LogicBotDashboard() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState('classes'); // classes, dashboard, student
  const [classes, setClasses] = useState([]);
  const [selectedClass, setSelectedClass] = useState(null);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newClassName, setNewClassName] = useState("");
  const [selectedStudent, setSelectedStudent] = useState(null);

  // 1. Autenticación
  useEffect(() => {
    const initAuth = async () => {
      // Login anónimo para el profesor en este demo
      await signInAnonymously(auth);
    };
    initAuth();
    const unsubscribe = onAuthStateChanged(auth, setUser);
    return () => unsubscribe();
  }, []);

  // 2. Cargar Clases del Docente
  useEffect(() => {
    if (!user) return;

    // Ruta: artifacts/{appId}/public/data/classes
    const q = collection(db, 'artifacts', appId, 'public', 'data', 'classes');

    const unsubscribe = onSnapshot(q, (snapshot) => {
      const classList = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
      setClasses(classList);
      setLoading(false);
    }, (error) => {
      console.error("Error cargando clases:", error);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [user]);

  // 3. Cargar Estudiantes cuando se selecciona una clase
  useEffect(() => {
    if (!selectedClass) {
      setStudents([]);
      return;
    }

    setLoading(true);
    // Ruta: artifacts/{appId}/public/data/users_sync
    // Aquí es donde el backend Python escribe los datos sincronizados
    const q = collection(db, 'artifacts', appId, 'public', 'data', 'users_sync');

    const unsubscribe = onSnapshot(q, (snapshot) => {
      let classStudents = snapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .filter(s => s.class_token === selectedClass.token);

      setStudents(classStudents);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching students", error);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [selectedClass]);

  // --- LÓGICA DE NEGOCIO ---

  const handleCreateClass = async () => {
    if (!newClassName.trim()) return;

    // Generar Token: Ej PROG-2025-X82
    const suffix = Math.random().toString(36).substring(2, 5).toUpperCase();
    const token = `PROG-${new Date().getFullYear()}-${suffix}`;

    try {
      await addDoc(collection(db, 'artifacts', appId, 'public', 'data', 'classes'), {
        name: newClassName,
        token: token,
        createdAt: new Date().toISOString(),
        teacherId: user.uid,
        studentCount: 0
      });
      setShowCreateModal(false);
      setNewClassName("");
    } catch (e) {
      console.error("Error creating class:", e);
    }
  };

  const calculateAutonomy = (student) => {
    if (!student.retos_completados || student.retos_completados === 0) return 0;
    const autonomos = student.retos_sin_pistas || 0;
    return Math.round((autonomos / student.retos_completados) * 100);
  };

  const getStatusColor = (score) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 50) return "bg-yellow-400";
    return "bg-red-400";
  };

  // --- VISTAS ---

  // 1. VISTA: LISTA DE CLASES
  const renderClassList = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Mis Aulas Virtuales</h2>
          <p className="text-gray-500">Gestiona tus grupos y monitorea el progreso.</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          <Plus size={20} /> Crear Clase
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.map((cls) => (
          <div
            key={cls.id}
            onClick={() => { setSelectedClass(cls); setView('dashboard'); }}
            className="group bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition cursor-pointer relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-2 h-full bg-blue-500 group-hover:bg-blue-600 transition"></div>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-gray-800">{cls.name}</h3>
              <div className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-sm font-mono font-bold">
                {cls.token}
              </div>
            </div>
            <div className="flex items-center gap-4 text-gray-500 text-sm">
              <div className="flex items-center gap-1">
                <Users size={16} />
                <span>{students.filter(s => s.class_token === cls.token).length || 0} alumnos</span>
              </div>
              <div className="flex items-center gap-1">
                <Activity size={16} />
                <span>Activos hoy</span>
              </div>
            </div>
          </div>
        ))}

        {classes.length === 0 && !loading && (
          <div className="col-span-full text-center py-12 bg-gray-50 rounded-xl border-dashed border-2 border-gray-200">
            <BookOpen className="mx-auto h-12 w-12 text-gray-400 mb-3" />
            <h3 className="text-lg font-medium text-gray-900">No tienes clases activas</h3>
            <p className="text-gray-500 mb-4">Crea tu primera clase para empezar a recibir alumnos.</p>
          </div>
        )}
      </div>
    </div>
  );

  // 2. VISTA: DASHBOARD DE CLASE (Matriz + Métricas)
  const renderClassDashboard = () => {
    const totalStudents = students.length;
    const activeStudents = students.filter(s => {
      if(!s.ultima_conexion) return false;
      return new Date(s.ultima_conexion).toDateString() === new Date().toDateString();
    }).length;

    return (
      <div className="space-y-8 animate-in fade-in duration-500">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <button
              onClick={() => { setSelectedClass(null); setView('classes'); }}
              className="text-gray-500 hover:text-gray-700 text-sm flex items-center gap-1 mb-1"
            >
              ← Volver a mis clases
            </button>
            <h1 className="text-3xl font-bold text-gray-900">{selectedClass.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-gray-500">Token de acceso:</span>
              <code className="bg-gray-100 px-2 py-0.5 rounded text-gray-800 font-mono font-bold">{selectedClass.token}</code>
              <button className="text-blue-600 hover:text-blue-800" onClick={() => navigator.clipboard.writeText(selectedClass.token)}>
                <Copy size={16} />
              </button>
            </div>
          </div>

          <div className="flex gap-3">
             <Card className="!p-3 flex items-center gap-3 min-w-[140px]">
               <div className="bg-blue-100 p-2 rounded-full text-blue-600"><Users size={20}/></div>
               <div>
                 <p className="text-xs text-gray-500">Total Alumnos</p>
                 <p className="text-xl font-bold">{totalStudents}</p>
               </div>
             </Card>
             <Card className="!p-3 flex items-center gap-3 min-w-[140px]">
               <div className="bg-green-100 p-2 rounded-full text-green-600"><Activity size={20}/></div>
               <div>
                 <p className="text-xs text-gray-500">Activos Hoy</p>
                 <p className="text-xl font-bold">{activeStudents}</p>
               </div>
             </Card>
          </div>
        </div>

        {/* Matriz de Habilidades (Heatmap) */}
        <Card>
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold flex items-center gap-2">
              <BookOpen className="text-blue-500" /> Matriz de Habilidades
            </h3>
            <div className="flex gap-2 text-xs">
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-green-500 rounded-sm"></div> Dominio</span>
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-400 rounded-sm"></div> En Proceso</span>
              <span className="flex items-center gap-1"><div className="w-3 h-3 bg-red-400 rounded-sm"></div> Riesgo</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg">Estudiante</th>
                  {TEMAS_JAVA.map(tema => (
                    <th key={tema} className="px-2 py-3 text-center truncate max-w-[100px]" title={tema}>
                      {tema.split(' ')[0]}...
                    </th>
                  ))}
                  <th className="px-4 py-3 rounded-tr-lg text-center">Autonomía</th>
                </tr>
              </thead>
              <tbody>
                {students.map((student) => {
                  const temas = JSON.parse(student.progreso_temas || '{}');
                  const autonomia = calculateAutonomy(student);

                  return (
                    <tr
                      key={student.id}
                      className="bg-white border-b hover:bg-gray-50 cursor-pointer transition"
                      onClick={() => { setSelectedStudent(student); setView('student'); }}
                    >
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {student.nombre}
                        <div className="text-xs text-gray-400">{student.numero_telefono}</div>
                      </td>
                      {TEMAS_JAVA.map(tema => {
                        const nivel = temas[tema]?.nivel || 1;
                        const score = (nivel / 5) * 100;
                        return (
                          <td key={tema} className="px-2 py-3 text-center">
                            <div className={`w-full h-8 rounded-md ${getStatusColor(score)} opacity-80 flex items-center justify-center text-white font-bold text-xs`}>
                              Lvl {nivel}
                            </div>
                          </td>
                        );
                      })}
                      <td className="px-4 py-3 text-center">
                        <Badge
                          type={autonomia > 75 ? 'success' : autonomia > 40 ? 'warning' : 'danger'}
                          text={`${autonomia}%`}
                        />
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {students.length === 0 && (
               <div className="text-center py-8 text-gray-500">
                 No hay estudiantes vinculados a esta clase aún.
                 <br/>
                 Pídeles que envíen: <code className="bg-gray-100 px-2 py-1 rounded">unirse {selectedClass.token}</code> al bot.
               </div>
            )}
          </div>
        </Card>

        {/* Panel de Integridad & Alertas */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-red-600">
              <ShieldAlert /> Auditoría de Integridad
            </h3>
            <div className="space-y-4">
              {students.filter(s => calculateAutonomy(s) < 40 && s.retos_completados > 5).map(s => (
                <div key={s.id} className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-100">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="text-red-500" size={18} />
                    <div>
                      <p className="font-bold text-red-900">{s.nombre}</p>
                      <p className="text-xs text-red-700">Alta dependencia de pistas ({100 - calculateAutonomy(s)}%)</p>
                    </div>
                  </div>
                  <button className="text-xs bg-white border border-red-200 px-2 py-1 rounded text-red-700 hover:bg-red-50">
                    Revisar
                  </button>
                </div>
              ))}
              {students.filter(s => calculateAutonomy(s) < 40).length === 0 && (
                <div className="flex flex-col items-center justify-center py-6 text-green-600">
                  <CheckCircle size={32} className="mb-2" />
                  <p>No se detectan riesgos de integridad graves.</p>
                </div>
              )}
            </div>
          </Card>

          <Card>
            <h3 className="text-lg font-bold flex items-center gap-2 mb-4 text-blue-600">
              <Award /> Top Estudiantes (Líderes)
            </h3>
            <div className="space-y-3">
              {[...students].sort((a,b) => b.puntos - a.puntos).slice(0, 3).map((s, idx) => (
                <div key={s.id} className="flex items-center gap-4 p-2 hover:bg-gray-50 rounded-lg transition">
                  <div className={`w-8 h-8 flex items-center justify-center rounded-full font-bold text-white ${idx === 0 ? 'bg-yellow-400' : idx === 1 ? 'bg-gray-300' : 'bg-orange-400'}`}>
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-gray-800">{s.nombre}</p>
                    <p className="text-xs text-gray-500">Nivel {s.nivel} • {s.puntos} pts</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-green-600">🔥 {s.racha_dias} días</span>
                  </div>
                </div>
              ))}
              {students.length === 0 && <p className="text-center text-gray-400 py-4">Sin datos suficientes.</p>}
            </div>
          </Card>
        </div>
      </div>
    );
  };

  // 3. VISTA: DETALLE DE ESTUDIANTE
  const renderStudentDetail = () => {
    if (!selectedStudent) return null;
    const historial = JSON.parse(selectedStudent.historial_chat || '[]');

    return (
      <div className="space-y-6 animate-in slide-in-from-right duration-300">
        <button
          onClick={() => setView('dashboard')}
          className="text-gray-500 hover:text-gray-700 text-sm flex items-center gap-1"
        >
          ← Volver al Dashboard
        </button>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white">
            <div className="flex justify-between items-start">
              <div>
                <h1 className="text-3xl font-bold">{selectedStudent.nombre}</h1>
                <p className="opacity-80 flex items-center gap-2 mt-1">
                  <Users size={16} /> {selectedStudent.numero_telefono}
                  <span className="mx-2">•</span>
                  <Clock size={16} /> Última vez: {selectedStudent.ultima_conexion}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold">{selectedStudent.puntos} pts</div>
                <div className="text-sm opacity-80">Nivel {selectedStudent.nivel}</div>
              </div>
            </div>
          </div>

          <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              {/* Code Playback / Historial Reciente */}
              <div>
                <h3 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                   <Search size={18} /> Code Playback (Últimas interacciones)
                </h3>
                <div className="bg-gray-50 rounded-lg border border-gray-200 p-4 max-h-[400px] overflow-y-auto space-y-3">
                  {historial.length === 0 ? (
                    <p className="text-gray-400 text-center italic">No hay historial reciente.</p>
                  ) : (
                    historial.map((msg, i) => (
                      <div key={i} className={`flex ${msg.usuario ? 'justify-end' : 'justify-start'}`}>
                         <div className={`max-w-[80%] rounded-lg p-3 text-sm ${msg.usuario ? 'bg-blue-100 text-blue-900 rounded-br-none' : 'bg-white border border-gray-200 text-gray-800 rounded-bl-none'}`}>
                            {msg.usuario && <p className="text-xs font-bold text-blue-700 mb-1">Alumno</p>}
                            {!msg.usuario && <p className="text-xs font-bold text-gray-500 mb-1">LogicBot</p>}
                            <pre className="whitespace-pre-wrap font-mono text-xs overflow-x-auto">
                              {msg.usuario || msg.bot}
                            </pre>
                         </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-6">
               <Card className="bg-gray-50">
                 <h4 className="font-bold text-gray-700 mb-3">Métricas de Integridad</h4>
                 <div className="space-y-4">
                   <div>
                     <div className="flex justify-between text-sm mb-1">
                       <span>Autonomía</span>
                       <span className="font-bold">{calculateAutonomy(selectedStudent)}%</span>
                     </div>
                     <div className="w-full bg-gray-200 rounded-full h-2">
                       <div
                         className={`h-2 rounded-full ${getStatusColor(calculateAutonomy(selectedStudent))}`}
                         style={{ width: `${calculateAutonomy(selectedStudent)}%` }}
                       ></div>
                     </div>
                     <p className="text-xs text-gray-500 mt-1">Retos resueltos sin pedir pistas</p>
                   </div>

                   <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                     <span className="text-sm text-gray-600">Retos Completados</span>
                     <span className="font-bold">{selectedStudent.retos_completados}</span>
                   </div>
                   <div className="flex justify-between items-center">
                     <span className="text-sm text-gray-600">Pistas Usadas</span>
                     <span className="font-bold text-orange-500">{selectedStudent.pistas_usadas || 0}</span>
                   </div>
                 </div>
               </Card>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading && !students.length && !classes.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-10 px-6 py-4 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 text-white p-2 rounded-lg">
            <BookOpen size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900">LogicBot <span className="text-blue-600">Educator</span></h1>
            <p className="text-xs text-gray-500">Torre de Control Docente</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="hidden md:block text-right">
            <p className="text-sm font-bold text-gray-800">Profesor Demo</p>
            <p className="text-xs text-gray-500">ID: {user?.uid?.slice(0,6)}...</p>
          </div>
          <button
             onClick={() => auth.signOut()}
             className="p-2 text-gray-400 hover:text-red-500 transition rounded-full hover:bg-gray-100"
             title="Cerrar Sesión"
          >
            <LogOut size={20} />
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        {view === 'classes' && renderClassList()}
        {view === 'dashboard' && renderClassDashboard()}
        {view === 'student' && renderStudentDetail()}
      </main>

      {/* Modals */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl animate-in fade-in zoom-in duration-200">
            <h3 className="text-xl font-bold mb-4">Crear Nueva Clase</h3>
            <p className="text-gray-500 text-sm mb-4">Se generará un Token único para que tus alumnos se unan.</p>

            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre de la Clase</label>
            <input
              type="text"
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none mb-6"
              placeholder="Ej. Fundamentos de Java - Grupo A"
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
              autoFocus
            />

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium"
              >
                Cancelar
              </button>
              <button
                onClick={handleCreateClass}
                disabled={!newClassName.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Crear Clase
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}