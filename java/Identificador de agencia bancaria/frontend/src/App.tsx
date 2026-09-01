import { useMemo, useState } from 'react';
import { Clipboard, Download, FileText, ListChecks, LoaderCircle, Play, Search, Trash2, Upload, X } from 'lucide-react';

// Tipos de dados
type Resultado = { nib: string; valores: Record<string, string> };
type Resposta = { arquivos: string[]; resultados: Resultado[] };
type Status = 'match' | 'discrepancia' | 'erro';

// Constante de API
const API_URL = 'http://localhost:8080/api/processar';

export default function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [nibs, setNibs] = useState('');
  const [resultado, setResultado] = useState<Resposta | null>(null);
  const [filtro, setFiltro] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');

  // Memoização de derivados
  const listaNibs = useMemo(() => nibs.split(/[,\s\r\n]+/).filter(Boolean), [nibs]);
  const linhas = resultado?.resultados.filter((linha) => linha.nib.includes(filtro)) ?? [];

  // Adiciona arquivos da seleção
  function adicionarArquivos(event: React.ChangeEvent<HTMLInputElement>) {
    setFiles((atuais) => [...atuais, ...Array.from(event.target.files ?? [])]);
    event.target.value = '';
  }

  // Processa arquivo e busca NIBs
  async function processar() {
    if (!files.length || !listaNibs.length) {
      setErro('Selecione arquivos e informe ao menos um NIB.');
      return;
    }

    setCarregando(true);
    setErro('');

    const dados = new FormData();
    files.forEach((file) => dados.append('files', file));
    dados.append('nibs', nibs);

    try {
      const response = await fetch(API_URL, { method: 'POST', body: dados });
      if (!response.ok) throw new Error('Não foi possível processar os arquivos.');
      setResultado(await response.json());
    } catch (error) {
      setErro(error instanceof Error ? error.message : 'Erro inesperado.');
    } finally {
      setCarregando(false);
    }
  }

  // Limpa todos os dados
  function limpar() {
    setFiles([]);
    setNibs('');
    setResultado(null);
    setFiltro('');
    setErro('');
  }

  // Determina status de uma linha de resultado
  function statusDaLinha(linha: Resultado): Status {
    const valores = resultado?.arquivos
      .map((arquivo) => linha.valores[arquivo])
      .filter(Boolean) ?? [];

    if (!valores.length) return 'erro';

    const todosPresentes = valores.length === resultado?.arquivos.length;
    const todosIguais = new Set(valores).size === 1;

    return todosPresentes && todosIguais ? 'match' : 'discrepancia';
  }

  // Coleta NIBs da área de transferência
  async function colarLista() {
    try {
      setNibs(await navigator.clipboard.readText());
    } catch {
      setErro('Não foi possível acessar a área de transferência.');
    }
  }

  // Exporta resultados para CSV
  function exportarCsv() {
    if (!resultado) return;

    const cabecalho = ['NIB Pesquisado', ...resultado.arquivos];
    const corpo = linhas.map((linha) => [
      linha.nib,
      ...resultado.arquivos.map((arquivo) => linha.valores[arquivo] ?? '-'),
    ]);

    const csv = [cabecalho, ...corpo]
      .map((linha) =>
        linha
          .map((item) => `"${item.replace(/"/g, '""')}"`)
          .join(';'),
      )
      .join('\n');

    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'resultado.csv';
    link.click();
    URL.revokeObjectURL(url);
  }

  return <main className="app-shell min-h-screen px-4 py-8 text-slate-800 md:px-10">
    <div className="mx-auto max-w-[900px]">
      <header className="mb-8 flex items-end justify-between gap-4 border-b border-slate-200 pb-6">
        <div><p className="eyebrow mb-2">Operação local</p><h1>Identificador de agência</h1><p className="mt-2 max-w-xl text-sm text-slate-500">Cruze dados de múltiplas fontes para validar agências.</p></div>
        <span className="status-chip hidden md:inline-flex"><span className="status-dot status-match" />Online</span>
      </header>
      <section className="grid gap-5 md:grid-cols-2">
        <div className="surface-card"><div className="section-heading"><div className="icon-badge"><Upload size={18} /></div><div><p className="eyebrow">Entrada</p><h2>Arquivos de origem</h2></div><span className="count-badge">{files.length}</span></div>
          <label className="upload-zone"><Upload size={24} /><span className="font-semibold">Adicionar arquivos</span><span className="text-xs text-slate-500">Selecione um ou mais arquivos .txt</span><input type="file" accept=".txt,text/plain" multiple className="hidden" onChange={adicionarArquivos} /></label>
          <ul className="mt-4 flex flex-wrap gap-2">{files.map((file, index) => <li key={`${file.name}-${index}`} className="file-pill"><FileText size={14} /><span className="truncate">{file.name}</span><button title="Remover arquivo" aria-label={`Remover ${file.name}`} onClick={() => setFiles(files.filter((_, i) => i !== index))}><X size={14} /></button></li>)}</ul>
        </div>
        <div className="surface-card"><div className="section-heading"><div className="icon-badge"><ListChecks size={18} /></div><div><p className="eyebrow">Consulta</p><h2>NIBs para buscar</h2></div><span className="count-badge">{listaNibs.length}</span></div><textarea value={nibs} onChange={(event) => setNibs(event.target.value)} placeholder="Cole os NIBs separados por espaço, vírgula ou quebra de linha" className="input-area" /><button onClick={colarLista} className="outline-button mt-3"><Clipboard size={15} />Colar lista</button></div>
      </section>
      <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row"><button onClick={processar} disabled={carregando} className="primary-button"><>{carregando ? <LoaderCircle className="animate-spin" size={18} /> : <Play size={18} />}</>Processar</button><button onClick={limpar} className="outline-button"><Trash2 size={16} />Limpar</button></div>{erro && <p className="error-message">{erro}</p>}
      {resultado && <section className="surface-card mt-8 p-0"><div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 p-5"><div><p className="eyebrow">Resultado</p><h2>Cruzamento concluído</h2></div><div className="flex flex-wrap gap-2"><label className="search-control"><Search size={16} /><input value={filtro} onChange={(event) => setFiltro(event.target.value)} placeholder="Filtrar NIB" /></label><button title="Exportar CSV" onClick={exportarCsv} className="outline-button"><Download size={15} />Exportar CSV</button></div></div><div className="table-wrap"><table className="result-table"><thead><tr><th>NIB pesquisado</th>{resultado.arquivos.map((arquivo) => <th key={arquivo}>{arquivo}</th>)}<th>Status</th></tr></thead><tbody>{linhas.map((linha) => { const status = statusDaLinha(linha); return <tr key={linha.nib}><td className="nib-cell">{linha.nib}</td>{resultado.arquivos.map((arquivo) => <td key={arquivo} className={!linha.valores[arquivo] ? 'missing-value' : ''}>{linha.valores[arquivo] ?? '-'}</td>)}<td><span className={`status-label status-${status}`}><span className={`status-dot status-${status}`} />{status === 'match' ? 'Match' : status === 'discrepancia' ? 'Discrepância' : 'Erro'}</span></td></tr>; })}</tbody></table></div></section>}
    </div>
  </main>;
}
