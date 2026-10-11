import styles from './LoadingSpinner.module.css'

/**
 * Spinning icon with a short label naming the operation, e.g. "Saving…".
 * The label is always visible, and role="status" has screen readers read it.
 *
 * @param {object} props
 * @param {string} props.label
 */
function LoadingSpinner({ label }) {
  return (
    <div className={styles.wrapper} role="status">
      <span className={styles.spinner} aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

export default LoadingSpinner
