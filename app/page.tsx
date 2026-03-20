import Link from "next/link"

export default function Page() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col justify-center gap-4 px-6 py-10">
      <h1 className="text-3xl font-semibold tracking-tight">Cotizador</h1>
      <p className="text-muted-foreground">
        Esta app Next.js es la interfaz principal. El backend está en Django.
      </p>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/login"
          className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-primary-foreground"
        >
          Ir a Login
        </Link>
      </div>
    </main>
  )
}