(function(){
  const video = document.getElementById('video')
  const startCam = document.getElementById('startCam')
  const startStream = document.getElementById('startStream')
  const stopStream = document.getElementById('stopStream')
  const resultEl = document.getElementById('result')
  let ws = null
  let interval = null

  startCam.addEventListener('click', async ()=>{
    try {
      const stream = await navigator.mediaDevices.getUserMedia({video:true})
      video.srcObject = stream
      await video.play()
    } catch(e){ alert('Cannot access camera: '+e.message) }
  })

  function blobToDataURL(blob){
    return new Promise(res=>{
      const r = new FileReader(); r.onload = ()=>res(r.result); r.readAsDataURL(blob)
    })
  }

  async function captureBlob(){
    const c = document.createElement('canvas')
    c.width = video.videoWidth || 640
    c.height = video.videoHeight || 480
    const ctx = c.getContext('2d')
    ctx.drawImage(video,0,0,c.width,c.height)
    return new Promise(res=>c.toBlob(res,'image/jpeg',0.8))
  }

  startStream.addEventListener('click', ()=>{
    if (ws) return
    const url = (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + location.host + '/ws'
    ws = new WebSocket(url)
    ws.onopen = ()=>{
      interval = setInterval(async ()=>{
        const b = await captureBlob();
        const data = await blobToDataURL(b)
        ws.send(JSON.stringify({frame: data}))
      }, 1200)
    }
    ws.onmessage = (e)=>{
      try{ resultEl.textContent = JSON.stringify(JSON.parse(e.data), null, 2) }
      catch{ resultEl.textContent = e.data }
    }
    ws.onclose = ()=>{ stopStream() }
  })

  stopStream.addEventListener('click', ()=>{ stopStream() })

  function stopStream(){
    if (interval) clearInterval(interval); interval = null
    if (ws){ ws.close(); ws = null }
  }
})();