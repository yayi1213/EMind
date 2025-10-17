<template>
  <div style="padding:20px;">
    <h1>Emotion Recognition (Demo)</h1>
    <video ref="video" autoplay playsinline width="640" height="480" style="border:1px solid #ccc"></video>
    <div style="margin-top:10px;">
      <button @click="startCamera">Start Camera</button>
      <button @click="startStream">Start Stream</button>
      <button @click="stopStream">Stop Stream</button>
    </div>
    <div style="margin-top:10px;">
      <p><strong>Last server result:</strong></p>
      <pre>{{ lastResult }}</pre>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      ws: null,
      lastResult: null,
      streamInterval: null,
    }
  },
  methods: {
    async startCamera() {
      const v = this.$refs.video
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      v.srcObject = stream
      await v.play()
    },
    startStream() {
      if (this.ws) return
      const url = (location.protocol === 'https:' ? 'wss' : 'ws') + '://localhost:8000/ws'
      this.ws = new WebSocket(url)
      this.ws.onopen = () => {
        console.log('ws open')
        const v = this.$refs.video
        this.streamInterval = setInterval(async () => {
          const blob = await this.captureFrameBlob()
          const b64 = await this.blobToBase64(blob)
          this.ws.send(JSON.stringify({ frame: b64 }))
        }, 1200)
      }
      this.ws.onmessage = (e) => {
        this.lastResult = e.data
      }
      this.ws.onclose = () => {
        console.log('ws closed')
        this.stopStream()
      }
    },
    stopStream() {
      if (this.streamInterval) clearInterval(this.streamInterval)
      this.streamInterval = null
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
    },
    captureFrameBlob() {
      const v = this.$refs.video
      const c = document.createElement('canvas')
      c.width = v.videoWidth || 640
      c.height = v.videoHeight || 480
      const ctx = c.getContext('2d')
      ctx.drawImage(v, 0, 0, c.width, c.height)
      return new Promise((res) => c.toBlob(res, 'image/jpeg', 0.8))
    },
    blobToBase64(blob) {
      return new Promise((res) => {
        const reader = new FileReader()
        reader.onload = () => res(reader.result)
        reader.readAsDataURL(blob)
      })
    }
  },
  beforeUnmount() {
    this.stopStream()
  }
}
</script>
