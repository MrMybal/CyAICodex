'use strict';
const imageState={editing:null,dirty:false,offset:0,sequence:0,previewURL:null};
async function refreshImageReferences(){
  const current=$('#assistant-image').value;
  const data=await api('/images?status=&limit=100');
  $('#assistant-image').innerHTML=uiFragment('<option value="">Aucune</option>')+data.items.map(i=>uiHTML`<option value="${i.id}">${esc(i.title)}</option>`).join('');
  $('#assistant-image').value=current;
}
async function refreshImages(){
  const sequence=++imageState.sequence;
  const filter=$('#image-context');const previous=filter.value;
  filter.innerHTML=contextOptions();filter.value=previous;
  const params=new URLSearchParams({q:$('#image-search').value,status:$('#image-status').value,limit:12,offset:imageState.offset,include_global:$('#image-global').checked,...contextParams(filter.value)});
  const data=await api('/images?'+params);
  if(sequence!==imageState.sequence)return;
  $('#image-count').textContent=data.total;
  $('#image-grid').innerHTML=data.items.map(i=>uiHTML`<button class="image-card" data-image="${i.id}"><div class="image-thumbnail"><img src="/api/images/${i.id}/preview" alt="${esc(i.title)}" loading="lazy"></div><div class="image-card-info"><span class="scope-badge">${esc(scopeName(i))}</span><h3>${esc(i.title)}</h3><p>${esc(i.description)}</p><div class="tags">${i.tags.slice(0,4).map(t=>uiHTML`<span class="tag">${esc(t)}</span>`).join('')}</div><small>${i.width} × ${i.height} · ${i.transparent?uiFragment('Fond transparent'):uiFragment('Fond opaque')} · v${i.version}</small></div></button>`).join('')||uiFragment('<div class="empty"><span class="empty-icon">▧</span><h2>Aucune image dans cette sélection</h2><p>Importez un logo, une référence visuelle ou une capture et précisez comment vos IA doivent l’utiliser.</p><button class="primary" data-import-image>＋ Importer une image</button></div>');
  $('#image-previous').disabled=imageState.offset===0;$('#image-next').disabled=imageState.offset+12>=data.total;
  $('#image-pagination').textContent=data.total?uiHTML`${imageState.offset+1}–${Math.min(imageState.offset+12,data.total)} sur ${data.total}`:uiText('0 image');
}
function imageScopeChoices(selected=''){
  const scope=$('#image-scope').value;
  $('#image-group-label').hidden=scope==='global';$('#image-scope-id').required=scope!=='global';
  $('#image-scope-id').innerHTML=uiFragment('<option value="">Choisir un groupe</option>')+(scope==='global'?'':state.catalog[scope==='type'?'types':'projects'].map(g=>uiHTML`<option value="${g.id}">${esc(g.name)}</option>`).join(''));
  $('#image-scope-id').value=selected;
}
function imagePreviewURL(url){
  if(imageState.previewURL){URL.revokeObjectURL(imageState.previewURL);imageState.previewURL=null;}
  $('#image-editor-preview').src=url||'/static/logo-cy-book-transparent.png';
  $('#image-editor-preview').hidden=!url;
}
async function openImageEditor(identifier=null){
  const data=identifier?await api('/images/'+identifier):null;
  imageState.editing=data;imageState.dirty=false;
  const form=$('#image-form');form.reset();$('#image-error').textContent='';
  $('#image-dialog-title').textContent=data?uiFragment('Ressource d’image'):uiFragment('Importer une image');
  $('#image-upload-label').hidden=!!data;form.elements.file.required=!data;
  for(const name of ['title','description','preserve','avoid','usage','source','category','scope','status'])if(data)form.elements[name].value=data[name];
  if(data)form.elements.tags.value=data.tags.join(', ');
  else{const [scope,id]=$('#image-context').value.split(':');if(id)form.elements.scope.value=scope;}
  imageScopeChoices(data?.scope_id||$('#image-context').value.split(':')[1]||'');
  imagePreviewURL(data?uiHTML`/api/images/${data.id}/preview`:'');
  $('#image-file-info').textContent=data?uiHTML`${data.width} × ${data.height} · ${(data.bytes/1024).toFixed(0)} Ko · ${data.transparent?uiFragment('Transparence présente'):uiFragment('Image opaque')}`:uiFragment('PNG, JPEG ou WebP · 20 Mo maximum');
  $('#image-original').hidden=!data;$('#image-original').href=data?uiHTML`/api/images/${data.id}/file?download=true`:'#';
  $('#use-image-assistant').hidden=!data;
  $('#image-history').hidden=!data;$('#image-history').open=false;$('#image-history-list').replaceChildren();
  $('#image-dialog').showModal();
}
function closeImageEditor(){if(imageState.dirty&&!confirm(uiFragment('Fermer sans enregistrer les modifications de cette ressource ?')))return;$('#image-dialog').close();imagePreviewURL('');}
document.addEventListener('click',guarded(async e=>{
  const image=e.target.closest('[data-image]');if(image)await openImageEditor(image.dataset.image);
  if(e.target.closest('[data-import-image]'))await openImageEditor();
  if(e.target.closest('[data-close-image]'))closeImageEditor();
}));
$('#image-dialog').addEventListener('cancel',e=>{e.preventDefault();closeImageEditor();});
$('#image-form').addEventListener('input',()=>imageState.dirty=true);
$('#image-scope').addEventListener('change',()=>imageScopeChoices());
$('#image-file').addEventListener('change',()=>{
  const file=$('#image-file').files[0];if(!file)return;
  if(file.size>20*1024*1024){$('#image-error').textContent=uiFragment('L’image doit faire 20 Mo maximum.');$('#image-file').value='';return;}
  imagePreviewURL('');imageState.previewURL=URL.createObjectURL(file);$('#image-editor-preview').src=imageState.previewURL;$('#image-editor-preview').hidden=false;
  $('#image-file-info').textContent=uiHTML`${file.name} · ${(file.size/1024).toFixed(0)} Ko`;
  if(!$('#image-form').elements.title.value)$('#image-form').elements.title.value=file.name.replace(/\.[^.]+$/,'');
});
$('#image-form').addEventListener('submit',async e=>{
  e.preventDefault();const form=e.currentTarget;const b=$('#save-image');b.disabled=true;$('#image-error').textContent='';
  try{
    const metadata=Object.fromEntries(new FormData(form));delete metadata.file;
    metadata.tags=metadata.tags.split(',').map(t=>t.trim()).filter(Boolean);if(metadata.scope==='global')metadata.scope_id='';
    if(imageState.editing){await send('/images/'+imageState.editing.id,{description:metadata,version:imageState.editing.version},'PUT');}
    else{
      const payload=new FormData();payload.append('file',form.elements.file.files[0]);payload.append('metadata',JSON.stringify(metadata));
      const response=await fetch('/api/images',{method:'POST',body:payload,credentials:'same-origin'});const data=await response.json();
      if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:uiFragment('Vérifiez le fichier et les champs de la ressource.'));
    }
    imageState.dirty=false;$('#image-dialog').close();imagePreviewURL('');notify(uiFragment('Image et consignes enregistrées.'));await Promise.all([refreshImages(),refreshImageReferences()]);
  }catch(err){$('#image-error').textContent=err.message;}finally{b.disabled=false;}
});
$('#image-history').addEventListener('toggle',guarded(async()=>{
  if(!$('#image-history').open||!imageState.editing)return;
  const entries=await api('/images/'+imageState.editing.id+'/history');$('#image-history-list').replaceChildren();
  for(const entry of entries){const row=document.createElement('div');row.className='history-row';const label=document.createElement('span');label.textContent=uiHTML`v${entry.version} · ${entry.author} · ${shortDate(entry.at)}`;const b=document.createElement('button');b.type='button';b.className='quiet';b.textContent=uiFragment('Reprendre');b.addEventListener('click',()=>{const form=$('#image-form');for(const name of ['title','description','preserve','avoid','usage','source','category','scope','status'])form.elements[name].value=entry.snapshot[name];form.elements.tags.value=entry.snapshot.tags.join(', ');imageScopeChoices(entry.snapshot.scope_id);imageState.dirty=true;notify(uiFragment('Anciennes consignes chargées. Enregistrez pour créer une nouvelle version.'));});row.append(label,b);$('#image-history-list').append(row);}
}));
$('#use-image-assistant').addEventListener('click',guarded(async()=>{
  if(imageState.dirty){notify(uiFragment('Enregistrez les nouvelles consignes avant de les transmettre à l’assistant.'));return;}
  const id=imageState.editing.id;$('#image-dialog').close();await changePage('assistant');await refreshImageReferences();
  if(!$$('#assistant-image option').some(o=>o.value===id))$('#assistant-image').add(new Option(imageState.editing.title,id));
  $('#assistant-image').value=id;$('#chat-input').focus();notify(uiFragment('Image sélectionnée pour votre prochaine demande.'));
}));
let imageSearchTimer;$('#image-search').addEventListener('input',()=>{clearTimeout(imageSearchTimer);imageSearchTimer=setTimeout(guarded(async()=>{imageState.offset=0;await refreshImages();}),180);});
for(const id of ['image-context','image-status','image-global'])$('#'+id).addEventListener('change',guarded(async()=>{imageState.offset=0;await refreshImages();}));
$('#image-previous').addEventListener('click',guarded(async()=>{imageState.offset=Math.max(0,imageState.offset-12);await refreshImages();}));
$('#image-next').addEventListener('click',guarded(async()=>{imageState.offset+=12;await refreshImages();}));
window.addEventListener('beforeunload',e=>{if(imageState.dirty&&$('#image-dialog').open){e.preventDefault();e.returnValue='';}});
