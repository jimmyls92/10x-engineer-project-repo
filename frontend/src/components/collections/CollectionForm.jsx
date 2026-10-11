import { useState } from 'react'
import Button from '../shared/Button.jsx'
import ErrorMessage from '../shared/ErrorMessage.jsx'
import LoadingSpinner from '../shared/LoadingSpinner.jsx'
import styles from './CollectionForm.module.css'

// The API's own limits (models.py:245-246), checked before anything is sent.
const NAME_MAX = 100
const DESCRIPTION_MAX = 500

/**
 * Check the fields and return a message per invalid field.
 *
 * @param {{name: string, description: string}} values
 * @returns {Record<string, string>} Empty when every field passes.
 */
function validate(values) {
  const errors = {}
  if (!values.name.trim()) errors.name = 'Name is required.'
  else if (values.name.length > NAME_MAX) errors.name = `Name must be ${NAME_MAX} characters or fewer.`
  if (values.description.length > DESCRIPTION_MAX) {
    errors.description = `Description must be ${DESCRIPTION_MAX} characters or fewer.`
  }
  return errors
}

/**
 * Form for a new collection, shown inside a Modal. What was typed stays here,
 * so a failed save keeps it, and the error is shown in the form.
 *
 * @param {object} props
 * @param {(data: {name: string, description: string|null}) => void} props.onSave
 * @param {() => void} props.onCancel
 * @param {boolean} props.busy True while the save request runs.
 * @param {Error|null} props.error The failed save, if any.
 */
function CollectionForm({ onSave, onCancel, busy, error }) {
  const [values, setValues] = useState({ name: '', description: '' })
  const [fieldErrors, setFieldErrors] = useState({})

  function update(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    const errors = validate(values)
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return
    onSave({ name: values.name, description: values.description || null })
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <label className={styles.field}>
        <span>Name</span>
        <input
          value={values.name}
          onChange={update('name')}
          aria-invalid={Boolean(fieldErrors.name)}
          aria-describedby={fieldErrors.name ? 'name-error' : undefined}
        />
        {fieldErrors.name && <span id="name-error" className={styles.fieldError}>{fieldErrors.name}</span>}
      </label>

      <label className={styles.field}>
        <span>Description (optional)</span>
        <input
          value={values.description}
          onChange={update('description')}
          aria-invalid={Boolean(fieldErrors.description)}
          aria-describedby={fieldErrors.description ? 'collection-description-error' : undefined}
        />
        {fieldErrors.description && (
          <span id="collection-description-error" className={styles.fieldError}>
            {fieldErrors.description}
          </span>
        )}
      </label>

      {error && <ErrorMessage error={error} resource="collection" />}
      {busy && <LoadingSpinner label="Saving…" />}

      <div className={styles.actions}>
        <Button onClick={onCancel} disabled={busy}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={busy}>
          Save
        </Button>
      </div>
    </form>
  )
}

export default CollectionForm
