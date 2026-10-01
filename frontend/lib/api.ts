const API=process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000/api'
export async function api(path:string,options:any={}){const r=await fetch(`${API}${path}`,{...options,headers:{'Content-Type':'application/json',...(options.headers||{})},cache:'no-store'});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||'Request failed')}return r.json()}
