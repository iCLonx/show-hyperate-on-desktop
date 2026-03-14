# show-hyperate-on-desktop
将hyperate页面显示在桌面上

## 功能
- 在桌面上显示来自 app.hyperate.io 页面的心率监测，用户可在对话框输入自己的设备ID
- 支持在 https://designer.hyperate.io/ 上生成的 OBS Browser Source URL 自定义图标显示
- 心率窗口背景透明且置顶
- 心率窗口可随鼠标拖动
- 支持切换窗口穿透

## 使用方法
- 运行 hpr.py 可以看见窗口，根据指示输入设备ID或者 url 并等待页面加载
- 若使用 Hyperate Widget Designer 网站自定义样式，请将图标置于画布的左上角

## 环境依赖
PyQt6 
PyQtWebEngine 
pywin32
