import { useEffect } from 'react'
import styles from './SuccessMessage.module.css'

// Long enough to read a short message; the close button dismisses it sooner.
const VISIBLE_MS = 4000

/**
 * Message confirming that a save or delete worked. It closes itself after
 * four seconds, or sooner with its close button. The parent keeps one message
 * at a time, so a new one replaces the old; giving each a new React key
 * restarts the timer even when the text repeats.
 *
 * @param {object} props
 * @param {string} props.message
 * @param {() => void} props.onClose Called when the message should disappear.
 */
function SuccessMessage({ message, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, VISIBLE_MS)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={styles.success} role="status">
      <span>{message}</span>
      <button type="button" className={styles.close} onClick={onClose} aria-label="Close message">
        ×
      </button>
    </div>
  )
}

export default SuccessMessage
