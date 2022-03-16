const swiper = new Swiper('.image-slider', {
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        scrollbar: {
            el: '.swiper-scrollbar',
        },
        autoHeight: true,
        hashNavigation: {
            watchState: true,
        },
    });

function fullscreen() {
    let redirect_url = window.location.href;
    redirect_url = redirect_url.replace('/photo/slider/', '/photo/image/');
    if (redirect_url.includes('#photo-'))
        redirect_url = redirect_url.replace('#photo-', '&photo_num=');
    window.location.href = redirect_url;
}

function closeSlider() {
    let redirect_url = window.location.href;
    if (redirect_url.includes('#photo-'))
        redirect_url = redirect_url.split('#photo-')[0];
    redirect_url = redirect_url.replace('/photo/slider/', '/photo/');
    window.location.href = redirect_url;
}
