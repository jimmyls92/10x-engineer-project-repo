import { NavLink } from 'react-router-dom'
import styles from './Header.module.css'

/** App name, and links to the two screens with the current one marked. */
function Header() {
  const linkClass = ({ isActive }) =>
    isActive ? `${styles.link} ${styles.active}` : styles.link

  return (
    <header className={styles.header}>
      <span className={styles.name}>PromptLab</span>
      <nav className={styles.nav}>
        {/* "end" keeps Prompts from staying marked on /collections, since "/" prefixes every path. */}
        <NavLink to="/" end className={linkClass}>
          Prompts
        </NavLink>
        <NavLink to="/collections" className={linkClass}>
          Collections
        </NavLink>
      </nav>
    </header>
  )
}

export default Header
