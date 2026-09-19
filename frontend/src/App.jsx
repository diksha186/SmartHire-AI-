import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'

import Home from './pages/Home'
import About from './pages/About'
import Login from './pages/Login'
import Register from './pages/Register'
import Jobs from './pages/Jobs'
import JobDetails from './pages/JobDetails'
import NotFound from './pages/NotFound'

import CandidateDashboard from './pages/candidate/Dashboard'
import CandidateProfile from './pages/candidate/Profile'
import ResumeUpload from './pages/candidate/ResumeUpload'
import Recommendations from './pages/candidate/Recommendations'
import MyApplications from './pages/candidate/Applications'

import EmployerDashboard from './pages/employer/Dashboard'
import CompanyProfile from './pages/employer/CompanyProfile'
import ManageJobs from './pages/employer/ManageJobs'
import JobForm from './pages/employer/JobForm'
import Applicants from './pages/employer/Applicants'

import AdminDashboard from './pages/admin/Dashboard'
import AdminUsers from './pages/admin/Users'
import AdminJobs from './pages/admin/Jobs'
import AdminApplications from './pages/admin/Applications'

export default function App() {
  return (
    <>
      <Navbar />
      <main className="pb-4">
        <Routes>
          {/* Public */}
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/:id" element={<JobDetails />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Candidate */}
          <Route path="/candidate" element={<ProtectedRoute allow={['candidate']}><CandidateDashboard /></ProtectedRoute>} />
          <Route path="/candidate/profile" element={<ProtectedRoute allow={['candidate']}><CandidateProfile /></ProtectedRoute>} />
          <Route path="/candidate/resume" element={<ProtectedRoute allow={['candidate']}><ResumeUpload /></ProtectedRoute>} />
          <Route path="/candidate/recommendations" element={<ProtectedRoute allow={['candidate']}><Recommendations /></ProtectedRoute>} />
          <Route path="/candidate/applications" element={<ProtectedRoute allow={['candidate']}><MyApplications /></ProtectedRoute>} />

          {/* Employer */}
          <Route path="/employer" element={<ProtectedRoute allow={['employer']}><EmployerDashboard /></ProtectedRoute>} />
          <Route path="/employer/profile" element={<ProtectedRoute allow={['employer']}><CompanyProfile /></ProtectedRoute>} />
          <Route path="/employer/jobs" element={<ProtectedRoute allow={['employer']}><ManageJobs /></ProtectedRoute>} />
          <Route path="/employer/jobs/new" element={<ProtectedRoute allow={['employer']}><JobForm /></ProtectedRoute>} />
          <Route path="/employer/jobs/:id/edit" element={<ProtectedRoute allow={['employer']}><JobForm /></ProtectedRoute>} />
          <Route path="/employer/jobs/:id/applicants" element={<ProtectedRoute allow={['employer']}><Applicants /></ProtectedRoute>} />

          {/* Admin */}
          <Route path="/admin" element={<ProtectedRoute allow={['admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute allow={['admin']}><AdminUsers /></ProtectedRoute>} />
          <Route path="/admin/jobs" element={<ProtectedRoute allow={['admin']}><AdminJobs /></ProtectedRoute>} />
          <Route path="/admin/applications" element={<ProtectedRoute allow={['admin']}><AdminApplications /></ProtectedRoute>} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}
