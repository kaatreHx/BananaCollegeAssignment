export function Loader({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="loader" role="status" aria-live="polite">
      <span className="loader-banana" aria-hidden="true">
        🍌
      </span>
      <span>{label}</span>
    </div>
  )
}

export function PageLoader() {
  return (
    <div className="page-loader">
      <Loader label="Peeling the next puzzle…" />
    </div>
  )
}
