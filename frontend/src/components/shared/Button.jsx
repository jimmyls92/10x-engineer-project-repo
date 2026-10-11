import styles from './Button.module.css'

/**
 * Every button in the app.
 *
 * @param {object} props
 * @param {'primary'|'secondary'|'danger'} [props.variant] Look of the button; secondary when absent.
 * @param {'button'|'submit'} [props.type] "submit" inside a form, so Enter saves it.
 * @param {boolean} [props.disabled] Set while the request the button started is running.
 * @param {() => void} [props.onClick]
 * @param {React.ReactNode} props.children The button's text.
 */
function Button({ variant = 'secondary', type = 'button', disabled = false, onClick, children }) {
  return (
    <button
      type={type}
      className={`${styles.button} ${styles[variant]}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

export default Button
