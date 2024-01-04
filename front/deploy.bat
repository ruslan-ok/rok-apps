del Z:\apps\static\assets\index-*.css
del Z:\apps\static\assets\index-*.js
del Z:\apps\rusel\react\templates\react\index.html
copy C:\Web\apps\rusel\front\dist\assets\index-*.css Z:\apps\static\assets\
copy C:\Web\apps\rusel\front\dist\assets\index-*.js Z:\apps\static\assets\
copy C:\Web\apps\rusel\front\dist\index.html Z:\apps\rusel\react\templates\react\

del C:\Web\apps\rusel\back\static\assets\index-*.css
del C:\Web\apps\rusel\back\static\assets\index-*.js
del C:\Web\apps\rusel\back\react\templates\react\index.html
copy C:\Web\apps\rusel\front\dist\assets\index-*.css C:\Web\apps\rusel\back\static\assets\
copy C:\Web\apps\rusel\front\dist\assets\index-*.js C:\Web\apps\rusel\back\static\assets\
copy C:\Web\apps\rusel\front\dist\index.html C:\Web\apps\rusel\back\react\templates\react\

echo Done