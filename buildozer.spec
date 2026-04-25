[app]

title = SH Vertex Admin Panel
package.name = shvertexadminpanel
package.domain = com.shvertex

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,csv,wav,ogg
version = 4

requirements = python3,kivy,requests,certifi,rsa,pyasn1,pyjnius

orientation = portrait
fullscreen = 0
icon.adaptive_foreground.filename = foreground.png
icon.adaptive_background.filename = background.png
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.enable_androidx = True

[buildozer]

log_level = 2
warn_on_root = 1