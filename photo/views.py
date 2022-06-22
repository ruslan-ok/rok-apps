import os, pathlib, urllib.parse, mimetypes
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.http import FileResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import APP_PHOTO, ROLE_PHOTO, ROLE_APP
from rusel.base.dir_views import BaseDirView
from rusel.files import storage_path, service_path
from photo.config import app_config
from photo.models import Photo
from photo.forms import PhotoForm

role = ROLE_PHOTO
app = ROLE_APP[role]

class FolderView(BaseDirView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'photo/folder.html'

    def get(self, request, *args, **kwargs):
        query = None
        folder = ''
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
            folder = self.request.GET.get('folder')
        if query:
            if folder:
                folder = '&folder=' + folder
            else:
                folder = ''
            return HttpResponseRedirect(reverse('index') + '?app=' + APP_PHOTO + folder + '&q=' + query)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.store_dir = photo_storage(self.request.user)
        context = super().get_context_data(**kwargs)
        if (self.config.cur_view_group.view_id == 'map'):
            self.template_name = 'photo/map.html'
        context['list_href'] = '/photo/'
        context['cur_folder'] = self.cur_folder
        context['add_item_template'] = 'base/add_item_upload.html'
        context['add_item_placeholder'] = '{}'.format(_('Upload photo'))
        return context

    def is_image(self, path):
        mt = mimetypes.guess_type(path)
        file_type = '???'
        if mt and mt[0]:
            file_type = mt[0]
        if '/' in file_type and (file_type.split('/')[0] == 'image' or file_type.split('/')[0] == 'video'):
            return True
        return False

    def scan_files(self):
        self.gps_data = []
        self.file_list = []
        files_path = self.cur_folder
        if files_path:
            files_path += '/'
        num = 0
        with os.scandir(self.store_dir + self.cur_folder) as it:
            for entry in it:
                if (entry.name.upper() == 'Thumbs.db'.upper()):
                    continue
                if entry.is_dir():
                    continue
                if not self.is_image(entry.path):
                    continue
                item = Entry(entry.name, entry.stat().st_size, num)
                num += 1
                self.file_list.append(item)
                if not Photo.objects.filter(user=self.request.user.id, path=files_path, name=entry.name).exists():
                    size, lat, lon = get_photo_size_and_gps(self.request.user, files_path, entry.name)
                    p = Photo.objects.create(user=self.request.user, path=files_path, name=entry.name, size=size, lat=lat, lon=lon)
                else:
                    p = Photo.objects.filter(user=self.request.user.id, path=files_path, name=entry.name).get()
                if (p.lat and p.lon):
                    self.gps_data.append({ 'id': p.id, 'num': num-1, 'lat': str(p.lat), 'lon': str(p.lon), 'name': p.name })
        return self.gps_data

    def get_view_qty(self, group, nav_item):
        if (group.view_id == 'preview'):
            return len(self.file_list)
        if (group.view_id == 'map'):
            return len(self.gps_data)
        return None

    def get_success_url(self, **kwargs):
        folder = ''
        if ('folder' in self.request.GET):
            folder = self.request.GET['folder']
        view = ''
        if ('view' in self.request.GET):
            view = self.request.GET['view']
        if view:
            view = '&view=' + view
        return reverse('photo:list') + '?folder=' + folder + view

    def init_store_dir(self, user):
        self.store_dir = get_storage(user, 'photo')

#----------------------------------
class PhotoView(FormView, LoginRequiredMixin):
    form_class = PhotoForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_name = 'photo/slider.html'

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        self.store_dir = photo_storage(self.request.user)
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/photo/'
        context['hide_add_item_input'] = True


        self.cur_folder = ''
        page_title = ''
        title = ''
        if ('folder' in self.request.GET):
            self.cur_folder = self.request.GET['folder']
            page_title = self.cur_folder.split('/')[-1:][0]
            title = self.cur_folder
        if not self.cur_folder:
            page_title = _('Photo bank')
            title = page_title
        context['title'] = title

        self.scan_files()
        context['file_list'] = self.file_list
        context['cur_folder'] = self.cur_folder
        return context

    def is_image(self, path):
        mt = mimetypes.guess_type(path)
        file_type = '???'
        if mt and mt[0]:
            file_type = mt[0]
        if '/' in file_type and (file_type.split('/')[0] == 'image' or file_type.split('/')[0] == 'video'):
            return True
        return False

    def scan_files(self):
        self.gps_data = []
        self.file_list = []
        with os.scandir(self.store_dir + self.cur_folder) as it:
            for entry in it:
                if (entry.name.upper() == 'Thumbs.db'.upper()):
                    continue
                if entry.is_dir():
                    continue
                if not self.is_image(entry.path):
                    continue
                self.file_list.append(entry.name)

#----------------------------------
class Entry:
    def __init__(self, name, size, num):
        self.name = name
        self.url = urllib.parse.quote_plus(name)
        self.size = size
        self.num = num

    def __repr__(self):
        return '{ url: ' + self.url + ', sz: ' + str(self.size) + ' }'

    def __eq__(self, other): 
        if not isinstance(other, Entry):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and self.size == other.size
        
# Служебные адреса для отображения фото
#----------------------------------
def get_storage(user, folder, service=False):
    if service:
        path = service_path.format(user.id) + '{}/'.format(folder)
    else:
        path = storage_path.format(user.username) + '{}/'.format(folder)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path

def photo_storage(user):
    return get_storage(user, 'photo')

def thumb_storage(user):
    return get_storage(user, 'thumbnails', True)

def mini_storage(user):
    return get_storage(user, 'photo_mini', True)

def get_name_from_request(request, param='file'):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get(param)
    if not query:
        return ''
    return urllib.parse.unquote_plus(query)

def get_photo(request): # Для отображения полноразмерного фото
    folder = get_name_from_request(request, 'folder')
    file = get_name_from_request(request, 'file')
    if (not file):
        photo_num = get_name_from_request(request, 'photo_num')
        file_list = []
        store_dir = photo_storage(request.user)
        with os.scandir(store_dir + folder) as it:
            for entry in it:
                if (entry.name.upper() == 'Thumbs.db'.upper()):
                    continue
                if entry.is_dir():
                    continue
                file_list.append(entry.name)
        file = file_list[int(photo_num)]
    path = photo_storage(request.user) + folder
    if folder:
        path += '/'
    fsock = open(path + file, 'rb')
    return FileResponse(fsock)

def get_thumb(request): # Для отображения миниатюры по имени файла
    folder = get_name_from_request(request, 'folder')
    file = get_name_from_request(request, 'file')
    if not file:
        return None
    build_thumb(request.user, folder, file)
    path = thumb_storage(request.user) + folder
    if folder:
        path += '/'
    fsock = open(path + file, 'rb')
    return FileResponse(fsock)

def get_mini(request, pk): # Для оторажения миниатюры на метке карты
    item = get_object_or_404(Photo.objects.filter(id=pk, user=request.user.id))
    build_mini(request.user, item)
    fsock = open(mini_storage(request.user) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

#----------------------------------
def build_thumb(user, folder, name):
    path = thumb_storage(user) + folder
    if not os.path.exists(path):
        os.makedirs(path)

    if folder:
        path += '/'
        folder += '/'

    if not os.path.exists(path + name):
        try:
            image = Image.open(photo_storage(user) + folder + name)
            exif_data = get_exif_data(image)
            if exif_data:
                lat, lon = get_lat_lon(exif_data)
                if lat and lon:
                    size = os.path.getsize(photo_storage(user) + folder + name)
                    get_photo_id(user, folder, name, size, lat, lon)
            image.thumbnail((240, 240), Image.ANTIALIAS)
            if ('exif' in image.info):
                exif = image.info['exif']
                image.save(path + name, exif=exif)
            else:
                image.save(path + name)
        except UnidentifiedImageError as e:
            pass

#----------------------------------
def build_mini(user, item):
    if not os.path.exists(mini_storage(user) + item.path):
        os.makedirs(mini_storage(user) + item.path)
    
    if not os.path.exists(mini_storage(user) + item.subdir() + item.name):
        try:
            image = Image.open(photo_storage(user) + item.subdir() + item.name)
            image.thumbnail((100, 100), Image.ANTIALIAS)
            if ('exif' in image.info):
                exif = image.info['exif']
                image.save(mini_storage(user) + item.subdir() + item.name, exif = exif)
            else:
                image.save(mini_storage(user) + item.subdir() + item.name)
        except UnidentifiedImageError as e:
            pass

#----------------------------------
def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
    
                    exif_data[decoded] = gps_data
                else:
                    exif_data[decoded] = value
    except AttributeError:
        pass
    return exif_data

#----------------------------------
def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
	
#----------------------------------
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])
    return d + (m / 60.0) + (s / 3600.0)
    
#----------------------------------
def get_lat_lon(exif_data):
    """Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)"""
    lat = None
    lon = None

    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon

#----------------------------------
def get_photo_id(user, path, name, size = None, lat = None, lon = None):
    if not Photo.objects.filter(name=name, path=path, user=user.id).exists():
        if (not size) or ((not lat) and (not lon)):
            size, lat, lon = get_photo_size_and_gps(user, path, name)
        item = Photo.objects.create(name=name, path=path, user=user, size=size, lat=lat, lon=lon)
    else:
        item = Photo.objects.filter(name=name, path=path, user=user.id).get()
        if (not size) or ((not lat) and (not lon)):
            size, lat, lon = get_photo_size_and_gps(user, path, name)
        if (not item.size) and size:
            item.size = size
            item.save()
        if (not item.lat) and (not item.lon) and lat and lon:
            item.lat = lat
            item.lon = lon
            item.save()
    return item.id

#----------------------------------
# Извлечение гео-координат из атрибутов изображения
def get_photo_size_and_gps(user, path, name):
    try:
        size = 0
        subdir = ''
        if path:
            subdir = path + '/'
        image = Image.open(photo_storage(user) + subdir + name)
        exif_data = get_exif_data(image)
        size = os.path.getsize(photo_storage(user) + subdir + name)
        if size or exif_data:
            lat = lon = None
            if exif_data:
                lat, lon = get_lat_lon(exif_data)
            return size, lat, lon
    except UnidentifiedImageError as e:
        pass
    return None, None, None

