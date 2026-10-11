import Header from './Header.jsx'
import styles from './Layout.module.css'

/**
 * Page frame: the header above the current screen.
 *
 * @param {object} props
 * @param {React.ReactNode} props.children The screen to show below the header.
 */
function Layout({ children }) {
  return (
    <>
      <Header />
      <main className={styles.main}>{children}</main>
    </>
  )
}

export default Layout
