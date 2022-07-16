import pymorphy2
from django.core.management.base import BaseCommand

from common.choices import LocalityType, StreetType
from common.models import Country, Region, Locality, District, Street


class Command(BaseCommand):
    help = 'Init localities from urkposhta localities csv file in Ukrainian language'

    def add_arguments(self, parser):
        parser.add_argument('-file', default='houses.csv')

    def make_region(self, name, country):
        return Region.objects.get_or_create(
            name_uk=name, country=country,
            defaults=dict(
                name=name,
                name_ru=name,
                name_uk=name,
                country=country,
            )
        )[0]

    def make_district(self, name, region):
        return District.objects.get_or_create(
            name_uk=name, region=region,
            defaults=dict(
                name=name,
                name_ru=name,
                name_uk=name,
                region=region,
            )
        )[0]

    def make_locality(self, name, l_type, district):

        if l_type in ['м', 'м.']:
            locality_type = LocalityType.CITY.value
        elif l_type in ['с', 'с.']:
            locality_type = LocalityType.VILLAGE.value
        elif l_type in ['смт', 'смт.']:
            locality_type = LocalityType.URBAN_VILLAGE.value
        else:
            locality_type = LocalityType.CITY.value

        return Locality.objects.get_or_create(
            name_uk=name, district=district, locality_type=locality_type,
            defaults=dict(
                name=name,
                name_ru=name,
                name_uk=name,
                district=district, locality_type=locality_type,
            )
        )[0]

    def make_street(self, name, s_type, locality):
        s_type = s_type.replace('.', '').strip()
        if s_type in ['алея']:
            street_type = StreetType.ALLEY.value
        elif s_type in ['бул', 'бульв', 'бульвар']:
            street_type = StreetType.BOULEVARD.value
        elif s_type in ['пров', 'провулок']:
            street_type = StreetType.LANE.value
        elif s_type in ['площа', 'пл']:
            street_type = StreetType.SQUARE.value
        elif s_type in ['просп', 'проспект']:
            street_type = StreetType.AVENUE.value
        else:
            street_type = StreetType.STREET.value

        return Street.objects.get_or_create(
            name_uk=name, locality=locality, street_type=street_type,
            defaults=dict(
                name=name,
                name_ru=name,
                name_uk=name,
                locality=locality, street_type=street_type,
            )
        )[0]

    def handle(self, *args, **options):
        file = options['file']
        morph = pymorphy2.MorphAnalyzer(lang='uk')

        country, created = Country.objects.get_or_create(name='Украина', name_ru='Украина', name_uk='Україна')

        cant_transform = set()

        with open(file, 'r', encoding='windows-1251') as f:
            content = f.readlines()
            for line in content[1:]:
                data = line.split(';')
                region_str = data[0]
                district_str = data[1]
                locality_str = data[2]
                street_str = data[4]

                # get locality type
                district_parts = district_str.split()
                locality_type = district_parts.pop(0)
                district_str = ' '.join(district_parts)
                # форма слова
                try:
                    district_str = morph.parse(district_str)[0].inflect({'masc'}).word.capitalize()
                except:
                    cant_transform.add(district_str)

                # get street type
                street_parts = street_str.split()
                street_type = street_parts.pop(0)
                street_str = ' '.join(street_parts)

                region = self.make_region(region_str, country)
                district = self.make_district(district_str, region)
                locality = self.make_locality(locality_str, locality_type, district)
                self.make_street(street_str, street_type, locality)

        if cant_transform:
            self.stdout.write('Can`t transform words: {}'.format(', '.join(cant_transform)))
