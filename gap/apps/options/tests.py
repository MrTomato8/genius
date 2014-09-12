"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import StringIO
import csv
from decimal import Decimal as D
from django.test import TestCase

from apps.basket.models import Basket
from apps.catalogue.models import Product, ProductClass
from apps.pricelist.utils import import_csv
from apps.partner.models import Partner

from apps.options.models import OptionChoice
from apps.options.calc.calculator import OptionsCalculator


class CalculatorTest(TestCase):
    product=None
    user=None
    def setUp(self):
        klass,_=ProductClass.objects.get_or_create(name="test")
        self.product,_=Product.objects.get_or_create(title="coca cola",product_class=klass)
        Partner.objects.get_or_create(name="test")

        csv_array=[]
        csv_array.append({
            'product':"coca cola",
            'size':"big",
            "quantity":"1",
            "quantity-discount":"1-0.00,10-10.00",
            "tpl_price":"0.8",
            "rpl_price":"1.2",
            "min_area":"0",
            "min_order":"1",
            })
        csv_array.append({
            'product':"coca cola",
            'size':"custom",
            "quantity":"1",
            "quantity-discount":"0.8-0.00,10-10.00",
            "tpl_price":"0.8",
            "rpl_price":"1",
            "min_area":"0.8",
            "min_order":"0.8",
            })
        fieldnames=[
            'product','size',"quantity",
            "quantity-discount","tpl_price",
            "rpl_price","min_area","min_order"]
        csvFile=StringIO.StringIO()
        writer = csv.DictWriter(csvFile,fieldnames=fieldnames)
        writer.writerow(dict((fn,fn) for fn in fieldnames))
        for row in csv_array:
            writer.writerow(row)

        csvFile.seek(0)
        import_csv(csvFile)
        self.user=Basket().owner

    def test_calculator_for_custom_area(self):
        #calculator accepts width and height in mm
        data={
            "quantity":"20",
            "number_of_files":1,
            "width":"1000","height":"800"}
        qs = OptionChoice.objects.filter(code="custom")
        assert(qs.count()==1)
        calculator=OptionsCalculator(self.product,qs,data)
        area=D("1")*D("0.8")*D(20)
        print calculator.total_price(self.user)
        print area*D(1)*D("0.9")

        assert(calculator.total_price(self.user)==area*D(1)*D("0.9"))

    def test_calculator(self):
        data={
            "quantity":"20",
            "number_of_files":1,
            "width":0,"height":0}
        qs = OptionChoice.objects.filter(code="big")
        assert(qs.count()==1)
        calculator=OptionsCalculator(self.product,qs,data)
        assert(calculator.total_price(self.user)==D(20)*D("0.9")*D("1.2"))




