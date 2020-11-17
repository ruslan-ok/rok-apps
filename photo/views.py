import os, shutil, urllib.parse
from operator import attrgetter
from PIL import Image, UnidentifiedImageError
from PIL.ExifTags import TAGS, GPSTAGS
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.urls import reverse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from hier.aside import Fix
from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import get_search_info, get_search_mode, set_article_kind, set_article_visible, set_restriction, set_content
from hier.files import storage_path, service_path, folder_path
from hier.models import get_app_params
from hier.categories import get_categories_list

from .models import app_name, Photo
from .forms import PhotoForm, FileForm

items_per_page = 12


# Режимы приложения
#----------------------------------
def main(request): # Фотографии в виде миниатюр
    return do_main(request, 'main')

def map(request): # Фотографии на карте
    return do_main(request, 'map')

def one(request): # Просмотр одной фотографии, заданной именем файла
    name = get_name_from_request(request)
    if name:
        dirs = name.split('/')
        sub_name = dirs[-1:][0]
        if (len(dirs) > 1):
            sub_path = name[:len(name)-len(sub_name)-1]
        else:
            sub_path = ''
        pk = get_photo_id(request.user, sub_path, sub_name)
        if pk:
            set_article_kind(request.user, app_name, '', pk)
            set_article_visible(request.user, app_name, False)
            return HttpResponseRedirect(reverse('photo:one'))
    app_param = get_app_params(request.user, app_name)
    return do_main(request, 'one', app_param.art_id)

# Навигация
#----------------------------------
def goto(request): # Опуститься в указанную папку
    set_article_visible(request.user, app_name, False)
    app_param = get_app_params(request.user, app_name)
    prefix = ''
    if app_param.content:
        prefix = app_param.content + '/'
    query = get_name_from_request(request)
    if query:
        set_content(request.user, app_name, prefix + query)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

def rise(request, level): # Подняться на указанный уровень вверх
    set_article_visible(request.user, app_name, False)
    if not level:
        set_content(request.user, app_name, '')
    else:
        app_param = get_app_params(request.user, app_name)
        crumbs = app_param.content.split('/')
        new_rest = ''
        cur_level = 1
        for crumb in crumbs:
            new_rest += crumb
            if (cur_level < level):
                new_rest += '/'
                cur_level += 1
            else:
                break
        set_content(request.user, app_name, new_rest)

    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

def by_id(request, pk): # Просмотр фотографии с указанным id
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    if item:
        set_article_kind(request.user, app_name, '', item.id)
        set_article_visible(request.user, app_name, False)
        return HttpResponseRedirect(reverse('photo:one'))
    return HttpResponseRedirect(reverse('photo:main'))

def form(request): # Отображение формы
    set_article_visible(request.user, app_name, True)
    return HttpResponseRedirect(reverse('photo:one'))


# Служебные адреса для отображения фото
#----------------------------------
def get_photo(request, pk): # Для отображения полноразмерного фото
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    fsock = open(photo_storage(request.user) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

def get_thumb(request): # Для отображения миниатюры по имени файла
    name = get_name_from_request(request)
    if not name:
        return None
    if (name == 'dir'):
        fsock = open(folder_path, 'rb')
    else:
        build_thumb(request.user, name)
        fsock = open(thumb_storage(request.user) + name, 'rb')
    return FileResponse(fsock)

def get_mini(request, pk): # Для оторажения миниатюры на метке карты
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    build_mini(request.user, item)
    fsock = open(mini_storage(request.user) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def do_main(request, restriction, pk = None, art_vis = False):
    
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('photo:' + restriction) + extract_get_params(request))

    set_restriction(request.user, app_name, restriction)

    item = None
    if (restriction == 'one') and pk:
        item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))

    app_param, context = get_base_context_ext(request, app_name, restriction, _('photos'))

    if (restriction == 'one') and (not item):
        item = get_object_or_404(Photo.objects.filter(id = app_param.art_id, user = request.user.id))


    redirect_rest = ''

    if (restriction == 'one'):
        valid_article = Photo.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if not valid_article:
            set_article_visible(request.user, app_name, False)
            return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))
        else:
            item = get_object_or_404(Photo.objects.filter(id = app_param.art_id, user = request.user.id))
            context['item'] = item
            context['title'] = item.name
            if app_param.article:
                disable_delete = (app_param.content == 'Trash')
                redirect_rest = edit_item(request, context, item, disable_delete)
    
    if redirect_rest:
        return HttpResponseRedirect(reverse('photo:' + redirect_rest) + extract_get_params(request))

    file_form = None

    if (request.method == 'POST'):
        if ('file-upload' in request.POST):
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                handle_uploaded_file(request.FILES['upload'], request.user, app_param.content)
                return HttpResponseRedirect(reverse('photo:' + restriction) + extract_get_params(request))

    if not file_form:
        file_form = FileForm()

    context['file_form'] = file_form

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    context['hide_add_item_input'] = True
    context['without_lists'] = True

    data, gps_data = filtered_sorted_list(request.user, app_param, query)
    context['gps_data'] = gps_data

    fixes = []
    fixes.append(Fix('main', _('thumbnails').capitalize(), 'rok/icon/all.png', '/photo/', len(data)))
    fixes.append(Fix('map', _('on the map').capitalize(), 'todo/icon/map.png', '/photo/map/', len(data)))
    context['fix_list'] = fixes

    bread_crumbs = []
    crumbs = app_param.content.split('/')
    if ((len(crumbs) > 0) and crumbs[0]) or (restriction == 'one'):
        bread_crumbs.append({ 'url': '/photo/rise/0/', 'name': '[{}]'.format(_('photobank').capitalize()) })

    level = 1
    for crumb in crumbs:
        if not crumb:
            continue
        if (level == len(crumbs)) and (restriction != 'one'):
            context['title'] = crumb
        else:
            url = '/photo/rise/{}/'.format(level)
            bread_crumbs.append({ 'url': url, 'name': crumb })
        level += 1
    context['bread_crumbs'] = bread_crumbs

    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template_name = 'photo/' + restriction + '.html'
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


#----------------------------------
def get_name_from_request(request):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get('file')
    if not query:
        return None
    return urllib.parse.unquote_plus(query)

#----------------------------------
def get_storage(user, folder, service = False):
    if service:
        return service_path.format(user.id) + '{}/'.format(folder)
    return storage_path.format(user.id) + '{}/'.format(folder)

def photo_storage(user):
    return get_storage(user, 'photo')

def thumb_storage(user):
    return get_storage(user, 'thumbnails', True)

def mini_storage(user):
    return get_storage(user, 'photo_mini', True)


#----------------------------------
class Entry:
    def __init__(self, is_dir, path, name, size):
        self.is_dir = is_dir
        self.path = path
        self.name = name
        if (is_dir == 0): # directory
            self.url = urllib.parse.quote_plus(name)
        else: # file
            subdir = ''
            if path:
                subdir = path + '/'
            self.url = urllib.parse.quote_plus(subdir + name)
        self.size = size

    def __repr__(self):
        return '{ url: ' + self.url + ', sz: ' + str(self.size) + ' }'

    def __eq__(self, other): 
        if not isinstance(other, Entry):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.is_dir == other.is_dir and self.path == other.path and self.name == other.name and self.size == other.size
        
#----------------------------------
def filtered_sorted_list(user, app_param, query):
    data, gps_data = filtered_list(user, app_param.content, query)
    return sorted(data, key = attrgetter('is_dir', 'name')), gps_data

def filtered_list(user, content, query = None):
    data = []
    gps_data = []
    
    dirname = photo_storage(user) + content
    if not os.path.exists(dirname):
        set_content(user, app_name, '')
        return data, gps_data

    with os.scandir(dirname) as it:
        for entry in it:
            if (entry.name.upper() == 'Thumbs.db'.upper()):
                continue
            stat = entry.stat()
            is_dir = 0 if entry.is_dir() else 1
            item = Entry(is_dir, content, entry.name, stat.st_size)
            # Можно сразу актуализировать записи в БД, но возможно это скажется на быстродействии.
            # Если не делать сразу, то актуализация произойдет в момет отрисовки миниатюры.
            # Не будет работать, если заменить файл, изменив его содержимое или размер, так как триггер для обновления - 
            # отсутствие файла с именем, для которого выполняется отрисовка миниатюры.
            # check_and_update(user, item)
            data.append(item)

    for p in Photo.objects.filter(user = user.id, path = content):
        e = Entry(1, p.path, p.name, p.size)
        #raise Exception(e, data[0], e in data)
        if e not in data:
            Photo.objects.filter(id = p.id).delete()

    photos = Photo.objects.filter(user = user.id, path = content)
    for p in photos:
        if (p.lat and p.lon):
            gps_data.append({ 'id': p.id, 'lat': str(p.lat), 'lon': str(p.lon), 'name': p.name })

    #raise Exception(len(data), len(gps_data), data, photos)
    return data, gps_data

#----------------------------------
def check_and_update(user, entry):
    if (entry.is_dir == 0): #directory
        return
    get_photo_id(user, entry.path, entry.name, entry.size)

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
def get_lat_lon(exif_data, user, path, name):
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
                lat, lon = get_lat_lon(exif_data, user, subdir, name)
            return size, lat, lon
    except UnidentifiedImageError as e:
        pass
    return None, None, None

#----------------------------------
def get_photo_id(user, path, name, size = None, lat = None, lon = None):
    #raise Exception('get_photo_id: ', path, name, size, lat, lon)
    if not Photo.objects.filter(name = name, path = path, user = user.id).exists():
        if (not size) or ((not lat) and (not lon)):
            size, lat, lon = get_photo_size_and_gps(user, path, name)
        item = Photo.objects.create(name = name, path = path, user = user, size = size, lat = lat, lon = lon)
    else:
        item = Photo.objects.filter(name = name, path = path, user = user.id).get()
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
def build_thumb(user, name):
    if os.path.exists(photo_storage(user) + name) and os.path.isdir(photo_storage(user) + name):
        return

    dirs = name.split('/')
    sub_dir = ''
    sub_name = dirs[-1:][0]
    if (len(dirs) > 1):
        sub_dir = name[:len(name)-len(sub_name)-1]
    
    if not os.path.exists(thumb_storage(user) + sub_dir):
        os.makedirs(thumb_storage(user) + sub_dir)
    
    if not os.path.exists(thumb_storage(user) + name):
        try:
            image = Image.open(photo_storage(user) + name)
            exif_data = get_exif_data(image)
            if exif_data:
                lat, lon = get_lat_lon(exif_data, user, sub_dir, sub_name)
                if lat and lon:
                    size = os.path.getsize(photo_storage(user) + name)
                    get_photo_id(user, sub_dir, sub_name, size, lat, lon)
            image.thumbnail((240, 240), Image.ANTIALIAS)
            if ('exif' in image.info):
                exif = image.info['exif']
                image.save(thumb_storage(user) + name, exif = exif)
            else:
                image.save(thumb_storage(user) + name)
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
def edit_item(request, context, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('article_delete' in request.POST):
            if delete_item(request, item, disable_delete):
                return 'main'
        if ('item-save' in request.POST):
            form = PhotoForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                if form.cleaned_data.get('category'):
                    if data.categories:
                        data.categories += ' '
                    data.categories += form.cleaned_data['category']
                form.save()
                return 'one'
        if ('category-delete' in request.POST):
            category = request.POST['category-delete']
            item.categories = item.categories.replace(category, '')
            item.save()
            return 'one'

    if not form:
        form = PhotoForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    context['categories'] = get_categories_list(item.categories)
    return ''

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    dst_path = photo_storage(request.user) + 'Trash/'
    if not os.path.exists(dst_path):
        os.mkdir(dst_path)
    src = photo_storage(request.user) + item.subdir() + item.name
    dst = dst_path + item.name
    shutil.move(src, dst)
    item.path = 'Trash'
    item.save()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def handle_uploaded_file(f, user, content):
    subdir = ''
    if content:
        subdir = content + '/'
    path = photo_storage(user) + subdir
    #raise Exception(path)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

