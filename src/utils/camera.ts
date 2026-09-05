export function explainCameraError(error: unknown): string {
  const name = error instanceof DOMException ? error.name : ''
  if (name === 'TimeoutError') {
    return '申请摄像头超时。Edge 可能把允许框弹在了后台，或相机驱动卡住。请看任务栏是否有权限提示，并关闭「相机」和会议软件后重试。'
  }
  if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
    return 'Edge 拒绝了摄像头。请点地址栏左侧小锁 → 网站权限 → 摄像头 → 允许，然后刷新。'
  }
  if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
    return '没有找到摄像头。本机应有 Integrated Camera，请在设备管理器中确认相机已启用。'
  }
  if (name === 'NotReadableError' || name === 'TrackStartError') {
    return '摄像头被占用。请关闭 Windows 相机、会议软件和其他打开本站的标签页。'
  }
  if (name === 'SecurityError' || name === 'NotSupportedError') {
    return '当前页面不能调用摄像头。请用 Edge 打开 http://127.0.0.1:5173/'
  }
  const message = error instanceof Error ? error.message : '未知错误'
  return `打开摄像头失败（${name || 'Error'}）：${message}`
}

export function requestCamera(timeoutMs = 10000): Promise<MediaStream> {
  if (!navigator.mediaDevices?.getUserMedia) {
    return Promise.reject(new DOMException('浏览器不支持摄像头', 'NotSupportedError'))
  }
  if (!window.isSecureContext) {
    return Promise.reject(new DOMException('需要安全上下文', 'SecurityError'))
  }
  const request = navigator.mediaDevices.getUserMedia({
    video: { width: { ideal: 640 }, height: { ideal: 360 }, frameRate: { ideal: 15 } },
    audio: false,
  })
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => {
      reject(new DOMException('申请摄像头超时', 'TimeoutError'))
    }, timeoutMs)
    request.then(
      (stream) => {
        window.clearTimeout(timer)
        resolve(stream)
      },
      (error) => {
        window.clearTimeout(timer)
        reject(error)
      },
    )
  })
}
