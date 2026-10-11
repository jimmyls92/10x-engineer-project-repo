import styles from './ErrorMessage.module.css'

/**
 * Pick the plain-language message for a failed request
 * (specs/frontend.md, "Loading, error and empty state behaviour").
 *
 * @param {number|null} status HTTP status, or null when the server was not reached.
 * @param {'prompt'|'collection'} resource What the request was about.
 * @returns {string}
 */
function plainMessage(status, resource) {
  if (status === null) return "Can't reach the server. Check your connection and try again."
  if (status === 404) return `This ${resource} no longer exists.`
  if (status === 400) return 'The selected collection no longer exists. Choose another one.'
  if (status === 422) return 'Some fields were rejected. Check them and try again.'
  return 'Something went wrong on the server. Try again.'
}

/**
 * A failed request, as a plain-language message with the status code under it.
 *
 * @param {object} props
 * @param {import('../../api/client.js').ApiError} props.error
 * @param {'prompt'|'collection'} props.resource What the request was about.
 */
function ErrorMessage({ error, resource }) {
  const status = error.status ?? null

  return (
    <div className={styles.error} role="alert">
      <p className={styles.message}>{plainMessage(status, resource)}</p>
      {status !== null && <p className={styles.code}>Error {status}</p>}
    </div>
  )
}

export default ErrorMessage
