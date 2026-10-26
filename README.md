# Folia iOS

把 [Folia](https://github.com/chthollyphile/folia-major)（Web 版）用 Capacitor 包成 iOS App，
在 GitHub Actions（macOS runner）上自动构建：

- `folia-ios.deb` — roothide 规范（iphoneos-arm64e），Sileo / Filza 直接安装
- `folia-ios-unsigned.ipa` — 未签名 ipa，可用 roothide 签名工具侧载

产物在每次构建的 Release 里。本地构建：`bash` 任意，直接推 main 触发 CI。

## CI 流程
1. 克隆 folia-major → `npm run build` 产出 Web dist
2. Capacitor 生成 iOS 壳工程（appId `com.corpsezhao.folia`）
3. Info.plist 打补丁：允许 HTTP、后台音频
4. xcodebuild 无签名 archive → Payload → ldid adhoc 签名
5. `scripts/make_deb.py` 手工打 deb（无需 dpkg）
