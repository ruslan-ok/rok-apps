import os, pathlib, glob, urllib.parse
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from task.const import ROLE_PHOTO, ROLE_APP
from rusel.base.views import BaseDirListView
from rusel.files import storage_path, service_path
from photo.config import app_config
from photo.models import Photo

role = ROLE_PHOTO
app = ROLE_APP[role]

class ListView(BaseDirListView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'photo/folder.html'

    def get_context_data(self, **kwargs):
        self.store_dir = photo_storage(self.request.user.id)
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/photo/'
        context['cur_folder'] = self.cur_folder
        return context

    def scan_files(self, file_list, path):
        gps_data = []
        with os.scandir(path) as it:
            for entry in it:
                if (entry.name.upper() == 'Thumbs.db'.upper()):
                    continue
                if entry.is_dir():
                    continue
                item = Entry(entry.name, entry.stat().st_size)
                file_list.append(item)

        # fd = glob.glob(path + '/*')
        # if not len(fd):
        #     return gps_data
        # for f in fd:
        #     ff = f.replace('\\', '/')
        #     name = ff.split(path)[1].strip('/')
        #     if (name.upper() == 'Thumbs.db'.upper()):
        #         continue
        #     item = Entry(name, self.sizeof_fmt(os.path.getsize(ff)))
        #     file_list.append(item)
        return gps_data

#----------------------------------
class Entry:
    def __init__(self, name, size):
        self.name = name
        self.url = urllib.parse.quote_plus(name)
        self.size = size

    def __repr__(self):
        return '{ url: ' + self.url + ', sz: ' + str(self.size) + ' }'

    def __eq__(self, other): 
        if not isinstance(other, Entry):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and self.size == other.size
        
# Служебные адреса для отображения фото
#----------------------------------
def get_storage(user_id: int, folder, service=False):
    if service:
        path = service_path.format(user_id) + '{}/'.format(folder)
    else:
        path = storage_path.format(user_id) + '{}/'.format(folder)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    return path

def photo_storage(user_id: int):
    return get_storage(user_id, 'photo')

def thumb_storage(user_id: int):
    return get_storage(user_id, 'thumbnails', True)

def mini_storage(user_id: int):
    return get_storage(user_id, 'photo_mini', True)

def get_name_from_request(request, param='file'):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get(param)
    if not query:
        return ''
    return urllib.parse.unquote_plus(query)

def get_photo(request, pk): # Для отображения полноразмерного фото
    item = get_object_or_404(Photo.objects.filter(id=pk, user=request.user.id))
    fsock = open(photo_storage(request.user.id) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

def get_thumb(request): # Для отображения миниатюры по имени файла
    folder = get_name_from_request(request, 'folder')
    name = get_name_from_request(request, 'file')
    if not name:
        return None
    build_thumb(request.user, folder, name)
    path = thumb_storage(request.user.id) + folder
    if folder:
        path += '/'
    fsock = open(path + name, 'rb')
    return FileResponse(fsock)

def get_mini(request, pk): # Для оторажения миниатюры на метке карты
    item = get_object_or_404(Photo.objects.filter(id=pk, user=request.user.id))
    build_mini(request.user.id, item)
    fsock = open(mini_storage(request.user.id) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

#----------------------------------
def build_thumb(user, folder, name):
    user_id = user.id
    # if os.path.exists(photo_storage(user_id) + name) and os.path.isdir(photo_storage(user_id) + name):
    #     return

    # dirs = folder.split('/')
    # sub_dir = ''
    # sub_name = dirs[-1:][0]
    # if (len(dirs) > 1):
    #     sub_dir = name[:len(name)-len(sub_name)-1]
    
    path = thumb_storage(user_id) + folder
    if not os.path.exists(path):
        os.makedirs(path)

    if folder:
        path += '/'
        folder += '/'

    if not os.path.exists(path + name):
        try:
            image = Image.open(photo_storage(user_id) + folder + name)
            exif_data = get_exif_data(image)
            if exif_data:
                lat, lon = get_lat_lon(exif_data)
                if lat and lon:
                    size = os.path.getsize(photo_storage(user_id) + folder + name)
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
def build_mini(user_id: int, item):
    if not os.path.exists(mini_storage(user_id) + item.path):
        os.makedirs(mini_storage(user_id) + item.path)
    
    if not os.path.exists(mini_storage(user_id) + item.subdir() + item.name):
        try:
            image = Image.open(photo_storage(user_id) + item.subdir() + item.name)
            image.thumbnail((100, 100), Image.ANTIALIAS)
            if ('exif' in image.info):
                exif = image.info['exif']
                image.save(mini_storage(user_id) + item.subdir() + item.name, exif = exif)
            else:
                image.save(mini_storage(user_id) + item.subdir() + item.name)
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

