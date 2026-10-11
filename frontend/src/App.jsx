import { Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout.jsx'
import PromptsPage from './components/prompts/PromptsPage.jsx'
import CollectionsPage from './components/collections/CollectionsPage.jsx'

/**
 * The app's two screens, one route each, inside the shared page frame.
 * Prompts is the default screen (specs/frontend.md, "Screens and their purpose").
 */
function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<PromptsPage />} />
        <Route path="/collections" element={<CollectionsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
