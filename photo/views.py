import os, urllib.parse
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
from hier.files import storage_path, folder_path
from hier.models import get_app_params

from .models import app_name, Photo
from .forms import PhotoForm

items_per_page = 12

def get_storage(user, folder):
    return storage_path.format(user.id) + '{}/'.format(folder)

def photo_storage(user):
    return get_storage(user, 'photo')

def thumb_storage(user):
    return get_storage(user, 'thumbnails')

def mini_storage(user):
    return get_storage(user, 'photo_mini')

#----------------------------------
class Entry:
    def __init__(self, is_dir, name, url, size, ctime):
        self.is_dir = is_dir
        self.name = name
        if (is_dir == 0):
            self.url = urllib.parse.quote_plus(name)
        else:
            self.url = url
        self.size = size
        self.ctime = ctime
        safe_url = urllib.parse.unquote_plus(url)

    def __repr__(self):
        return self.url
        
#----------------------------------
def all(request):
    set_restriction(request.user, app_name, '')
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def map(request):
    set_restriction(request.user, app_name, 'map')
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def show(request):
    return show_or_edit(request, False)

#----------------------------------
def edit(request):
    return show_or_edit(request, True)

#----------------------------------
def edit_id(request, pk):
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    set_restriction(request.user, app_name, '')
    return HttpResponseRedirect(reverse('photo:edit') + '?file=' + item.subdir() + item.name)

#----------------------------------
def goto(request):
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    app_param = get_app_params(request.user, app_name)
    query = ''
    prefix = ''
    if app_param.content:
        prefix = app_param.content + '/'
    if (request.method == 'GET'):
        query = request.GET.get('file')
    if query:
        set_content(request.user, app_name, prefix + query)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def jump(request, level):
    set_restriction(request.user, app_name, '')
    set_article_kind(request.user, app_name, '')
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

#----------------------------------
def photo(request, pk):
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    fsock = open(photo_storage(request.user) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

#----------------------------------
def mini(request, pk):
    item = get_object_or_404(Photo.objects.filter(id = pk, user = request.user.id))
    get_mini(request.user, item)
    fsock = open(mini_storage(request.user) + item.subdir() + item.name, 'rb')
    return FileResponse(fsock)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

    app_param, context = get_base_context_ext(request, app_name, 'main', _('photos'))

    redirect = False

    if (app_param.kind == 'photo'):
        valid_article = Photo.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if not valid_article:
            set_article_kind(request.user, app_name, '')
            set_article_visible(request.user, app_name, False)
            redirect = True
        else:
            item = get_object_or_404(Photo.objects.filter(id = app_param.art_id, user = request.user.id))
            context['item'] = item
            context['title'] = item.name
            if app_param.article:
                redirect = edit_item(request, context, item, False)
    
    if redirect:
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    context['hide_add_item_input'] = True

    data, gps_data = filtered_sorted_list(request.user, app_param, query)
    context['gps_data'] = gps_data

    fixes = []
    fixes.append(Fix('', _('thumbnails').capitalize(), 'rok/icon/all.png', 'all/', len(data)))
    fixes.append(Fix('map', _('on the map').capitalize(), 'todo/icon/map.png', 'map/', len(data)))
    context['fix_list'] = fixes

    bread_crumbs = []
    crumbs = app_param.content.split('/')
    if ((len(crumbs) > 0) and crumbs[0]) or (app_param.kind == 'photo'):
        bread_crumbs.append({ 'url': 'level/0/', 'name': '[ / ]' })

    level = 1
    for crumb in crumbs:
        if not crumb:
            continue
        if (level == len(crumbs)) and (app_param.kind == ''):
            context['title'] = crumb
        else:
            url = 'level/{}/'.format(level)
            bread_crumbs.append({ 'url': url, 'name': crumb })
        level += 1
    context['bread_crumbs'] = bread_crumbs

    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    if (app_param.kind == 'photo'):
        template_name = 'photo/photo.html'
    else:
        if (app_param.restriction == 'map'):
            template_name = 'photo/map.html'
        else:
            template_name = 'photo/list.html'
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


def filtered_sorted_list(user, app_param, query):
    data, gps_data = filtered_list(user, app_param.content, query)
    return sorted(data, key = attrgetter('is_dir', 'name')), gps_data

def filtered_list(user, content, query = None):
    data = []
    gps_data = []
    photos = Photo.objects.filter(user = user.id, path = content)
    for p in photos:
        if (p.lat and p.lon):
            gps_data.append({ 'id': p.id, 'lat': str(p.lat), 'lon': str(p.lon), 'name': p.name })
    
    dirname = photo_storage(user) + content
    if not os.path.exists(dirname):
        set_content(user, app_name, '')
        return data, []

    subdir = ''
    if content:
        subdir = content + '/'

    with os.scandir(dirname) as it:
        for entry in it:
            url = urllib.parse.quote_plus(subdir + entry.name)
            stat = entry.stat()
            is_dir = 0 if entry.is_dir() else 1
            data.append(Entry(is_dir, entry.name, url, stat.st_size, stat.st_ctime))
    return data, gps_data

#----------------------------------
def get_exif_data(image):
    """Returns a dictionary from the exif data of an PIL Image item. Also converts the GPS Tags"""
    exif_data = {}
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

    return exif_data

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
def get_photo_gps(user, path, name):
    try:
        subdir = ''
        if path:
            subdir = path + '/'
        image = Image.open(photo_storage(user) + subdir + name)
        exif_data = get_exif_data(image)
        if exif_data:
            return get_lat_lon(exif_data, user, subdir, name)
    except UnidentifiedImageError as e:
        pass
    return None, None

#----------------------------------
def get_photo_id(user, path, name, lat = None, lon = None):
    if not Photo.objects.filter(name = name, path = path, user = user.id).exists():
        if (not lat) and (not lon):
            lat, lon = get_photo_gps(user, path, name)
        item = Photo.objects.create(name = name, path = path, user = user, lat = lat, lon = lon)
    else:
        item = Photo.objects.filter(name = name, path = path, user = user.id).get()
        if (not lat) and (not lon):
            lat, lon = get_photo_gps(user, path, name)
        if (not item.lat) and (not item.lon) and lat and lon:
            item.lat = lat
            item.lon = lon
            item.save()
    return item.id

#----------------------------------
def show_or_edit(request, do_edit):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get('file')
    if not query:
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))
    name = urllib.parse.unquote_plus(query)
    image_path = ''
    if (name == 'dir'):
        image_path = folder_path
        name = ''

    try:
        if not do_edit:
            if (name != ''):
                image_path =thumb_storage(request.user)
                get_thumbnail(request.user, name)
            fsock = open(image_path + name, 'rb')
            return FileResponse(fsock)
        dirs = name.split('/')
        sub_name = dirs[-1:][0]
        if (len(dirs) > 1):
            sub_path = name[:len(name)-len(sub_name)-1]
        else:
            sub_path = ''
        pk = get_photo_id(request.user, sub_path, sub_name)
        set_article_kind(request.user, app_name, 'photo', pk)
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))
    except IOError:
        return HttpResponseNotFound()


#----------------------------------
def get_thumbnail(user, name):
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
                    get_photo_id(user, sub_dir, sub_name, lat, lon)
            image.thumbnail((240, 240), Image.ANTIALIAS)
            if ('exif' in image.info):
                exif = image.info['exif']
                image.save(thumb_storage(user) + name, exif = exif)
            else:
                image.save(thumb_storage(user) + name)
        except UnidentifiedImageError as e:
            pass

#----------------------------------
def get_mini(user, item):
    if not os.path.exists(mini_storage(user) + item.path):
        os.makedirs(mini_storage(user) + item.path)
    
    if not os.path.exists(mini_storage(user) + item.subdir() + item.name):
        try:
            image = Image.open(photo_storage(user) + item.subdir() + item.name)
            image.thumbnail((100, 100), Image.ANTIALIAS)
            image.save(mini_storage(user) + item.subdir() + item.name)
        except UnidentifiedImageError as e:
            pass

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
def edit_item(request, context, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('item-save' in request.POST):
            form = PhotoForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = PhotoForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return True

