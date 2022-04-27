/*
Drag and drop code strongly inspired in
https://css-tricks.com/drag-and-drop-file-uploading/
 */

(function() {
    let button = document.querySelector('.upload-button');
    let test = document.querySelector('div.test');
    let image = document.querySelector('div.image');
    let prediction = document.querySelector('div.prediction');
    let elapsedBox = document.querySelector('div.results-time');

    function getBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
          let encoded = reader.result.toString().replace(/^data:(.*,)?/, '');
          if ((encoded.length % 4) > 0) {
            encoded += '='.repeat(4 - (encoded.length % 4));
          }
          resolve(encoded);
        };
        reader.onerror = error => reject(error);
      });
    }

    let upload = function(image_as_b64) {
        const message = {
            'image': image_as_b64,
            'color-mappings': {
                'knot': [255, 0, 0],
                'crack': [0, 255, 0],
                'stain': [0, 0, 255]
            }
        };

        const start = performance.now();

        let request = new XMLHttpRequest();

        request.onreadystatechange = () => {
            if(request.readyState === 4) {
                if(request.status === 200) {
                    const end = performance.now();
                    const elapsed = Math.round((end - start) / 10) / 100
                    elapsedBox.textContent = `Tiempo de respuesta: ${elapsed} segundos`;

                    const response_message = JSON.parse(request.responseText);
                    const pred = response_message.data;
                    let pred_img = document.createElement('img')
                    pred_img.src = "data:image/png;base64," + pred;
                    prediction.replaceChildren(pred_img);

                    let img = document.createElement('img')
                    img.src = "data:image/png;base64," + image_as_b64;
                    image.replaceChildren(img);
                } else {
                    console.log(request.responseText);
                }
            }
        }

        request.open('POST', '/detect_defects');
        request.setRequestHeader('Content-Type', 'application/json');
        request.send(JSON.stringify(message));
    }

    let upload_and_test = function(file) {
        getBase64(file)
            .then((fdata) => {
                upload(fdata)
            });
    };

    ['drag', 'dragstart', 'dragend', 'dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        button.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        button.addEventListener(eventName, (e) => {
            test.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'dragend', 'drop'].forEach(eventName => {
        button.addEventListener(eventName, (e) => {
            test.classList.remove('dragover');
        }, false);
    });

    ['drop'].forEach(eventName => {
        button.addEventListener(eventName, (e) => {
            const file = e.dataTransfer.files[0];
            upload_and_test(file)
        }, false);
    });
})();