function selectPhrase(phraseId) {
    let listItem = document.getElementById(`phrase-${phraseId}`);
    if (!listItem)
        return;
    let form = document.getElementById('prase-edit-form');
    if (form)
        form.setAttribute('data-bs-phrase-id', phraseId);
    for (var i = 0; i < listItem.children.length; i++) {
        let phrase;
        switch(listItem.children[i].tagName) {
            case 'DIV': phrase = listItem.children[i].children[0]; break;
            case 'P':  phrase = listItem.children[i]; break;
        }
        if (phrase) {
            const phraseId = phrase.getAttribute('data-bs-lang-phrase-id');
            const lang = phrase.childNodes[0].innerText.replace(':', '').replace(' ', '');
            const text = phrase.childNodes[1] == undefined ? '' : phrase.childNodes[1].textContent;
            let phraseInput = document.getElementById(`${lang}-text`);
            if (phraseInput) {
                phraseInput.value = text;
                phraseInput.setAttribute('data-bs-lang-phrase-id', phraseId);
            }
        }
    }
}

async function savePhrases(django_host_api) {
    const form = document.getElementById('prase-edit-form');
    if (!form)
        return;
    const phraseId = form.getAttribute('data-bs-phrase-id');
    var data = {
        phraseId: phraseId,
        langPhrase: []
    };
    for (var i = 0; i < form.children.length; i++) {
        const phraseInput = form.children[i].children[1];
        if (phraseInput && phraseInput.tagName == 'INPUT') {
            let lp = {
                id: phraseInput.getAttribute('data-bs-lang-phrase-id'),
                lang: phraseInput.id.replace('-text', ''),
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
                const lang = phrase.childNodes[0].innerText.replace(':', '').replace(' ', '');
                let p_langPhrase = respData.data.langPhrase.filter(x => x.lang == lang)[0];
                phrase.setAttribute('data-bs-lang-phrase-id', p_langPhrase.id);
                phrase.childNodes[1].textContent = p_langPhrase.text == undefined ? '' : p_langPhrase.text;
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

    let url_parts = window.location.href.split('?');
    let redirect_url = url_parts[0];
    if (url_parts.length > 1) {
        if (!url_parts[1].includes('phrase'))
            url_parts[1] += '&phrase=' + respData.data.phraseId;
        else {
            let params = url_parts[1].split('&');
            url_parts[1] = '';
            for (var i = 0; i < params.length; i ++) {
                if (url_parts[1] != '')
                    url_parts[1] += '&';
                if (!params[i].includes('phrase'))
                    url_parts[1] += params[i];
                else
                    url_parts[1] += 'phrase=' + respData.data.phraseId;
            }
        }
        redirect_url += '?' + url_parts[1];
    }
    window.location.href = redirect_url;
}

async function deletePhrases(django_host_api) {
    const form = document.getElementById('prase-edit-form');
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