// Adiciona preview instantâneo + drag-and-drop nos campos de imagem do admin.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('input[type="file"][accept*="image"], input[type="file"][name$="image"]').forEach(function (input) {
    var wrapper = document.createElement('div');
    wrapper.className = 'se-upload-dropzone';
    wrapper.style.cssText = 'border:2px dashed #ccc;border-radius:8px;padding:14px;margin-top:8px;text-align:center;font-size:12px;color:#666;cursor:pointer;';
    wrapper.textContent = 'Arraste uma imagem aqui ou clique para selecionar';
    input.parentNode.insertBefore(wrapper, input);
    input.style.display = 'none';
    wrapper.addEventListener('click', function () { input.click(); });

    ['dragenter', 'dragover'].forEach(function (evt) {
      wrapper.addEventListener(evt, function (e) {
        e.preventDefault();
        wrapper.style.borderColor = '#D4AF37';
      });
    });
    ['dragleave', 'drop'].forEach(function (evt) {
      wrapper.addEventListener(evt, function (e) {
        e.preventDefault();
        wrapper.style.borderColor = '#ccc';
      });
    });
    wrapper.addEventListener('drop', function (e) {
      var files = e.dataTransfer.files;
      if (files.length) {
        input.files = files;
        input.dispatchEvent(new Event('change'));
      }
    });

    input.addEventListener('change', function () {
      var existingPreview = wrapper.querySelector('img');
      if (existingPreview) existingPreview.remove();
      if (input.files && input.files[0]) {
        var img = document.createElement('img');
        img.style.cssText = 'max-height:120px;border-radius:6px;margin-top:8px;display:block;margin-left:auto;margin-right:auto;';
        img.src = URL.createObjectURL(input.files[0]);
        wrapper.appendChild(img);
        wrapper.firstChild.textContent = input.files[0].name;
      }
    });
  });
});
