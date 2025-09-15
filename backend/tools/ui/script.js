async function getJSON(url) {
  const r = await fetch(url)
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

async function postJSON(url, body) {
  const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  if (!r.ok) throw new Error(await r.text())
  return r.json()
}

// ENV
const ENV_KEYS = [
  'DOMAIN', 'ACME_EMAIL', 'SECRET_KEY', 'POSTGRES_PASSWORD',
  'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GITHUB_REPOSITORY', 'IMAGE_TAG'
]

const envGrid = document.getElementById('envGrid')
const envPath = document.getElementById('envPath')
const envStatus = document.getElementById('envStatus')
const reloadEnv = document.getElementById('reloadEnv')
const saveEnv = document.getElementById('saveEnv')
// Production & Traefik
const prodDomain = document.getElementById('prodDomain')
const prodEmail = document.getElementById('prodEmail')
const saveProd = document.getElementById('saveProd')
const prodStatus = document.getElementById('prodStatus')

function renderEnvInputs(values) {
  envGrid.innerHTML = ''
  ENV_KEYS.forEach((k) => {
    const wrap = document.createElement('div')
    const label = document.createElement('label'); label.textContent = k
    const input = document.createElement('input'); input.value = values[k] || ''; input.id = `env_${k}`
    wrap.appendChild(label); wrap.appendChild(input)
    envGrid.appendChild(wrap)
  })
}

async function loadEnv() {
  envStatus.textContent = 'Loading...'
  try {
    const data = await getJSON('/api/vars')
    renderEnvInputs(data.env)
    envPath.textContent = data.file
    // populate prod section
    prodDomain.value = data.env.DOMAIN || ''
    prodEmail.value = data.env.ACME_EMAIL || ''
    envStatus.textContent = ''
  } catch (e) {
    envStatus.textContent = `Error: ${e}`
  }
}

reloadEnv.addEventListener('click', loadEnv)
saveEnv.addEventListener('click', async () => {
  const updates = {}
  ENV_KEYS.forEach((k) => {
    const v = document.getElementById(`env_${k}`).value
    updates[k] = v
  })
  envStatus.textContent = 'Saving...'
  try {
    const res = await postJSON('/api/vars', { updates })
    envStatus.innerHTML = `<span class="ok">Saved .env</span>`
  } catch (e) {
    envStatus.innerHTML = `<span class="err">Save failed: ${e}</span>`
  }
})

function isValidDomain(d) {
  // basic domain check (no protocol, has dot)
  return /^[a-z0-9.-]+\.[a-z]{2,}$/i.test(d)
}

function isValidEmail(e) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)
}

saveProd.addEventListener('click', async () => {
  const d = (prodDomain.value || '').trim()
  const m = (prodEmail.value || '').trim()
  if (!isValidDomain(d)) {
    prodStatus.innerHTML = '<span class="err">Enter a valid domain (e.g., example.com)</span>'
    return
  }
  if (!isValidEmail(m)) {
    prodStatus.innerHTML = '<span class="err">Enter a valid email (e.g., admin@example.com)</span>'
    return
  }
  prodStatus.textContent = 'Saving...'
  try {
    await postJSON('/api/vars', { updates: { DOMAIN: d, ACME_EMAIL: m } })
    // mirror into env grid if present
    const domEl = document.getElementById('env_DOMAIN'); if (domEl) domEl.value = d
    const emailEl = document.getElementById('env_ACME_EMAIL'); if (emailEl) emailEl.value = m
    prodStatus.innerHTML = '<span class="ok">Saved</span>'
  } catch (e) {
    prodStatus.innerHTML = `<span class="err">Save failed: ${e}</span>`
  }
})

// GHCR
const ghUser = document.getElementById('ghUser')
const ghToken = document.getElementById('ghToken')
const ghLogin = document.getElementById('ghLogin')
const ghStatus = document.getElementById('ghStatus')
const ghOutput = document.getElementById('ghOutput')

ghLogin.addEventListener('click', async () => {
  ghStatus.textContent = 'Logging in...'
  ghOutput.hidden = true; ghOutput.textContent = ''
  try {
    const res = await postJSON('/api/ghcr-login', { username: ghUser.value, token: ghToken.value })
    ghStatus.innerHTML = res.code === 0 ? '<span class="ok">Login OK</span>' : '<span class="err">Login failed</span>'
    ghOutput.hidden = false
    ghOutput.textContent = `stdout:\n${res.stdout}\n\nstderr:\n${res.stderr}`
  } catch (e) {
    ghStatus.innerHTML = `<span class="err">${e}</span>`
  }
})

// Run commands
const runnerSel = document.getElementById('runner')
const nameSel = document.getElementById('name')
const argsInput = document.getElementById('args')
const runBtn = document.getElementById('runBtn')
const runOutput = document.getElementById('runOutput')

let scripts = { make: [], pnpm: [] }

function populateNames() {
  const runner = runnerSel.value
  const items = scripts[runner] || []
  nameSel.innerHTML = ''
  items.forEach((n) => { const opt = document.createElement('option'); opt.value = n; opt.textContent = n; nameSel.appendChild(opt) })
}

runnerSel.addEventListener('change', populateNames)

async function loadScripts() {
  const data = await getJSON('/api/scripts')
  scripts = data
  populateNames()
}

runBtn.addEventListener('click', async () => {
  runBtn.disabled = true
  runOutput.textContent = 'Running...'
  try {
    const args = (argsInput.value || '').trim()
    const arr = args ? args.split(/\s+/) : []
    const res = await postJSON('/api/run', { runner: runnerSel.value, name: nameSel.value, args: arr })
    runOutput.textContent = `$ ${res.cmd}\n\n${res.stdout}\n${res.stderr ? '\n[stderr]\n' + res.stderr : ''}\n\n(exit code: ${res.code})`
  } catch (e) {
    runOutput.textContent = `Error: ${e}`
  } finally {
    runBtn.disabled = false
  }
})

// init
loadEnv()
loadScripts()
