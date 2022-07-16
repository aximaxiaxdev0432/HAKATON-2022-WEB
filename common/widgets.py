from django.forms import TextInput


class PhoneWidget(TextInput):
    def render(self, name, value, attrs=None, renderer=None):
        script = f'''
        jQuery(function($){{
         $("input[id*='id_{name}']").mask("+79999999999");
       }});
        '''
        if not attrs:
            attrs = {}
        attrs.update({"class": ' '.join(['phone-input', attrs.get('class', '')])})
        # print('attrs.update', super().render(name, value, attrs, renderer))
        return f'''
        {super().render(name, value, attrs, renderer)}
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.mask/1.14.10/jquery.mask.js"></script>                  
         <script>
        {script}
        </script> '''

