  $(document).ready(function() {
      // ✅ Initialize Select2 on the correct field (id_lab)
      let select = $('#id_lab').select2({
          theme: 'bootstrap4',
          placeholder: "Search and select Lab",
          allowClear: true,
          width: '100%',
          minimumResultsForSearch: 0
      });

      // ✅ Hide all results initially
      select.on('select2:open', function() {
          $('.select2-results__options').hide(); // hide results initially

          // ✅ Wait for user input before showing options
          $('.select2-search__field').off('input').on('input', function() {
              let searchText = $(this).val().trim();
              if (searchText.length > 1) {
                  $('.select2-results__options').show();
              } else {
                  $('.select2-results__options').hide();
              }
          });
      });
  });

  document.addEventListener('DOMContentLoaded', function() {
      function togglePasswordVisibility(toggleId, inputId) {
          const toggleIcon = document.getElementById(toggleId);
          const passwordInput = document.getElementById(inputId);

          toggleIcon.addEventListener('click', function() {
              const isPwd = passwordInput.type === 'password';
              passwordInput.type = isPwd ? 'text' : 'password';
              this.classList.toggle('fa-eye');
              this.classList.toggle('fa-eye-slash');
              this.classList.toggle('visible', isPwd); // add class when revealed
          });
      }

      togglePasswordVisibility('togglePassword1', 'password1');
      togglePasswordVisibility('togglePassword2', 'password2');
  });