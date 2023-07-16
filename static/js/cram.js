function selectPhrase(phraseId) {
    let listItem = document.getElementById(`phrase-${phraseId}`);
    if (!listItem)
        return;
    let form = document.getElementById('phrase-edit-form');
    if (form) {
        form.setAttribute('data-bs-phrase-id', phraseId);
        form.classList.remove('d-none');
    }
    for (var i = 0; i < listItem.children.length; i++) {
        let phrase;
        switch(listItem.children[i].tagName) {
            case 'DIV': phrase = listItem.children[i].children[0]; break;
            case 'P':  phrase = listItem.children[i]; break;
        }
        if (phrase) {
            const phraseId = phrase.getAttribute('data-bs-lang-phrase-id');
            let lang;
            let text;
            if (phrase.tagName == 'H5') {
                lang = 'ru';
                text = phrase.childNodes[0] == undefined ? '' : phrase.childNodes[0].textContent;
            } else {
                lang = phrase.childNodes[0].innerText.replace(':', '').replace(' ', '');
                text = phrase.childNodes[1] == undefined ? '' : phrase.childNodes[1].textContent;
            }
            let phraseInput = document.getElementById(`${lang}-text`);
            if (phraseInput) {
                phraseInput.value = text;
                phraseInput.setAttribute('data-bs-lang-phrase-id', phraseId);
            }
        }
    }
}

async function savePhrases(django_host_api) {
    const form = document.getElementById('phrase-edit-form');
    if (!form)
        return;
    const phraseId = form.getAttribute('data-bs-phrase-id');
    var data = {
        phraseId: phraseId,
        langPhrase: []
    };
    for (var i = 0; i < form.children.length; i++) {
        const phraseLabel = form.children[i].children[0];
        const phraseInput = form.children[i].children[1];
        if (phraseInput && phraseInput.tagName == 'TEXTAREA') {
            let lp = {
                id: phraseInput.getAttribute('data-bs-lang-phrase-id'),
                lang: phraseLabel.id.replace('-label', ''),
                text: phraseInput.value
            };
            data.langPhrase.push(lp);
        }
    }

    const url = `${django_host_api}/en/api/cram/phrase/${phraseId}/save_all/?format=json`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'PUT',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    const response = await fetch(url, options);
    const respData = await response.json();

    if (!response.ok) {
        const mess = `HTTP error! Status: ${response.status}`;
        iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
        throw new Error(mess);
    }

    let listItem = document.getElementById(`phrase-${respData.data.phraseId}`);
    if (listItem) {
        for (var i = 0; i < listItem.children.length; i++) {
            let phrase;
            switch(listItem.children[i].tagName) {
                case 'DIV': phrase = listItem.children[i].children[0]; break;
                case 'P':  phrase = listItem.children[i]; break;
            }
            if (phrase) {
                let phraseText;
                if (phrase.tagName == 'H5') {
                    lang = 'ru';
                    phraseText = phrase.childNodes[0].innerText;
                } else {
                    lang = phrase.childNodes[0].innerText.replace(':', '').replace(' ', '');
                    phraseText = phrase.childNodes[1].innerText;
                }
                let p_langPhrase = respData.data.langPhrase.filter(x => x.lang == lang)[0];
                phrase.setAttribute('data-bs-lang-phrase-id', p_langPhrase.id);
                phraseText.textContent = p_langPhrase.text == undefined ? '' : p_langPhrase.text;
            }
        }
    }

    for (var i = 0; i < form.children.length; i++) {
        let phrase;
        switch(form.children[i].tagName) {
            case 'DIV': phrase = form.children[i].children[0]; break;
            case 'P':  phrase = form.children[i]; break;
        }
        if (phrase) {
            const lang = phrase.innerText;
            let p_langPhrase = respData.data.langPhrase.filter(x => x.lang == lang)[0];
            let phraseInput = document.getElementById(`${lang}-text`);
            if (phraseInput) {
                phraseInput.setAttribute('data-bs-lang-phrase-id', p_langPhrase.id);
            }
        }
    }

    let url_parts_1 = window.location.href.split('?');
    let url_parts_2 = url_parts_1[0].split('/cram/phrases/');
    let url_parts_3 = url_parts_2[1].split('/');
    if (url_parts_3[1].length == 0)
        url_parts_3.splice(1, 0, respData.data.phraseId);
    else
        url_parts_3[1] = respData.data.phraseId;
    url_parts_2[1] = url_parts_3.join('/');
    url_parts_1[0] = url_parts_2.join('/cram/phrases/');
    let redirect_url = url_parts_1.join('?');
    window.location.href = redirect_url;
}

async function deletePhrases(django_host_api) {
    const form = document.getElementById('phrase-edit-form');
    if (!form)
        return;
    const phraseId = form.getAttribute('data-bs-phrase-id');
    const url = `${django_host_api}/en/api/cram/phrase/${phraseId}/?format=json`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
    };
    const response = await fetch(url, options);

    if (!response.ok) {
        const mess = `HTTP error! Status: ${response.status}`;
        iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
        throw new Error(mess);
    }

    let url_parts = window.location.href.split('?');
    let redirect_url = url_parts[0];
    if (url_parts.length > 1) {
        let params = url_parts[1].split('&');
        url_parts[1] = '';
        for (var i = 0; i < params.length; i ++) {
            if (!params[i].includes('phrase')) {
                if (url_parts[1] != '')
                    url_parts[1] += '&';
                url_parts[1] += params[i];
            }
        }
        if (url_parts[1])
            redirect_url += '?' + url_parts[1];
    }
    window.location.href = redirect_url;
}

let trainingStart;

function startTimer() {
    let el = document.getElementById('training-time-id');
    if (!el)
        return;
    let s_start = el.getAttribute('data-bs-start').replace(' ', 'T');
    trainingStart = new Date(s_start);
    setInterval(function() {
        var delta = Math.floor((Date.now() - trainingStart) / 1000);
        showDelta(delta);
    }, 1000);
    var delta = Math.floor((Date.now() - trainingStart) / 1000);
    showDelta(delta);
}

function showDelta(delta) {
    var h = Math.floor(delta / 3600);
    var m = Math.floor((delta - h * 3600) / 60);
    var s = delta - h * 3600 - m * 60;
    let el = document.getElementById('training-time-id');
    el.innerText = (h ? h + ':' : '') + checkTime(m) + ':' + checkTime(s);
}

function checkTime(i) {
    if (i < 10)
        i = '0' + i;  // add zero in front of numbers < 10
    return i;
}