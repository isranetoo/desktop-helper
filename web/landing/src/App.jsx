const RELEASE_BASE = 'https://github.com/isranetoo/desktop-helper/releases/download/v1.0.0/'

const platforms = [
  {
    name: 'Windows',
    href: `${RELEASE_BASE}sortify-windows.exe`,
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor" aria-hidden="true">
        <path d="M2 3.5l9.3-1.3V11H2V3.5zm10.7-1.5L22 0v11h-9.3V2zM2 12.9h9.3v8.8L2 20.4v-7.5zm10.7 0H22v11l-9.3-1.3v-9.7z" />
      </svg>
    )
  },
  {
    name: 'macOS',
    href: `${RELEASE_BASE}Sortify-macos.zip`,
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor" aria-hidden="true">
        <path d="M16.6 12.8c0-2.6 2.1-3.9 2.2-4-.1-.2-1.3-1.9-3.4-1.9-1.4 0-2.7.8-3.4.8-.7 0-1.7-.8-2.9-.7-1.5 0-2.9.9-3.7 2.2-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.8 3-.8s1.8.8 3 .8c1.2 0 2-.1 3.5-2.4.5-.8.8-1.5 1-2-.1-.1-3.4-1.3-3.4-4.6zm-2-7.1c.6-.7 1-1.7.9-2.7-.9 0-1.9.6-2.5 1.3-.5.6-1 1.6-.9 2.6 1 .1 1.9-.5 2.5-1.2z" />
      </svg>
    )
  },
  {
    name: 'Linux',
    href: `${RELEASE_BASE}sortify-linux.AppImage`,
    icon: (
      <svg viewBox="0 0 24 24" className="h-6 w-6" fill="currentColor" aria-hidden="true">
        <path d="M12 2c-2.1 0-3.6 2.1-3.6 4.6 0 1.4.5 2.8 1.3 3.8-.9.7-2.2 1.8-2.2 3.8 0 1.2.5 2.3 1.2 3.2-.5.7-.7 1.4-.7 2.3 0 1.4 1 2.3 2.3 2.3.8 0 1.6-.4 2-.9.4.5 1.2.9 2 .9 1.4 0 2.3-1 2.3-2.3 0-.9-.3-1.7-.7-2.3.7-.9 1.2-2 1.2-3.2 0-2-1.3-3.1-2.2-3.8.8-1 1.3-2.4 1.3-3.8C15.6 4.1 14.1 2 12 2zm-1.2 4.5c.5 0 .9.4.9.9s-.4.9-.9.9-.9-.4-.9-.9.4-.9.9-.9zm2.4 0c.5 0 .9.4.9.9s-.4.9-.9.9-.9-.4-.9-.9.4-.9.9-.9z" />
      </svg>
    )
  }
]

export default function App() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <header className="mb-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-sortify-blue to-sortify-blueDark shadow-glow">
            <span className="text-lg font-black text-white">S</span>
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-sortify-accent">Sortify</p>
            <h1 className="text-lg font-semibold text-white">Desktop Helper</h1>
          </div>
        </div>
        <a
          href="#downloads"
          className="rounded-full border border-sortify-blue/40 px-5 py-2 text-sm font-medium text-sortify-accent transition hover:border-sortify-accent hover:bg-sortify-blue/10"
        >
          Baixar agora
        </a>
      </header>

      <section className="grid items-center gap-10 md:grid-cols-[1.2fr_1fr]">
        <div>
          <p className="mb-4 inline-flex rounded-full border border-sortify-blue/40 bg-sortify-blue/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-sortify-accent">
            organização inteligente de arquivos
          </p>
          <h2 className="text-4xl font-bold leading-tight text-white md:text-5xl">
            Seu desktop limpo em minutos com o poder do <span className="text-sortify-blue">Sortify</span>.
          </h2>
          <p className="mt-6 max-w-xl text-lg text-slate-300">
            O Sortify organiza automaticamente pastas como Downloads e Desktop usando regras por extensão,
            data e nome. Tenha produtividade sem perder tempo movendo arquivo por arquivo.
          </p>

          <div id="downloads" className="mt-10 flex flex-wrap gap-4">
            {platforms.map((platform) => (
              <a
                key={platform.name}
                href={platform.href}
                className="group inline-flex items-center gap-3 rounded-2xl border border-slate-800 bg-sortify-card px-5 py-3 text-white transition hover:-translate-y-0.5 hover:border-sortify-blue hover:shadow-glow"
              >
                <span className="text-sortify-accent transition group-hover:text-sortify-blue">{platform.icon}</span>
                <span className="text-sm font-semibold">Baixar para {platform.name}</span>
              </a>
            ))}
          </div>
          <p className="mt-3 text-sm text-slate-400">
            Os botões baixam arquivos do release mais recente no GitHub para cada plataforma.
          </p>
        </div>

        <div className="rounded-3xl border border-sortify-blue/20 bg-sortify-card/90 p-7 shadow-glow backdrop-blur">
          <h3 className="text-xl font-semibold text-white">Por que usar o Sortify?</h3>
          <ul className="mt-5 space-y-4 text-slate-300">
            <li className="rounded-xl border border-slate-800 bg-black/20 p-4">📂 Organização por categorias e subpastas por data.</li>
            <li className="rounded-xl border border-slate-800 bg-black/20 p-4">⚡ Monitoramento em tempo real para manter tudo em ordem.</li>
            <li className="rounded-xl border border-slate-800 bg-black/20 p-4">↩️ Undo persistente para desfazer operações com segurança.</li>
            <li className="rounded-xl border border-slate-800 bg-black/20 p-4">🧠 Regras personalizadas para fluxos profissionais e pessoais.</li>
          </ul>
        </div>
      </section>
    </main>
  )
}
