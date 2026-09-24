[app]

title = Pharmacy Pro
package.name = pharmacypro
package.domain = org.pharmacy

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,db,pdf

version = 1.0

requirements = python3,kivy,reportlab

orientation = portrait

fullscreen = 0

android.api = 35
android.minapi = 23

android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = True


[buildozer]

log_level = 2
warn_on_root = 1
