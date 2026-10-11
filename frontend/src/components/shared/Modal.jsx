import { useEffect, useRef } from 'react'
import styles from './Modal.module.css'

/**
 * The floating window for forms, confirmations and error pop-ups.
 *
 * Built on the browser's <dialog>: opened with showModal(), it keeps keyboard
 * focus inside the window and closes on Escape. The parent shows the window by
 * rendering it and hides it by removing it.
 *
 * @param {object} props
 * @param {string} props.title Heading of the window, also its accessible name.
 * @param {() => void} props.onClose Called on Escape; the parent decides what closing means.
 * @param {React.ReactNode} props.children The window's content.
 */
function Modal({ title, onClose, children }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    dialog.showModal()
    return () => dialog.close()
  }, [])

  // Escape fires "cancel". Left alone, the browser would close the dialog while
  // the parent still renders it, so the parent is asked to close it instead.
  function handleCancel(event) {
    event.preventDefault()
    onClose()
  }

  return (
    <dialog
      ref={dialogRef}
      className={styles.dialog}
      aria-labelledby="modal-title"
      onCancel={handleCancel}
    >
      <h2 id="modal-title" className={styles.title}>
        {title}
      </h2>
      {children}
    </dialog>
  )
}

export default Modal
