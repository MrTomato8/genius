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
        # pass on command line but not on test, strange really
        data={
            "quantity":20,
            "number_of_files":1,
            "width":"1000","height":"800"
            }
        qs = OptionChoice.objects.filter(code="custom")
        assert(qs.count()==1)

        product,_=Product.objects.get_or_create(title="coca cola")
        calculator=OptionsCalculator(product,qs,data)
        calculator.custom=True #little hack
        area=D("1")*D("0.8")*D("20")
        if not calculator.total_price(None)==area*D(1)*D("0.9"):
            error=[
                calculator.total_price(self.user),
                area*D(1)*D("0.9"),
                calculator.calculate_custom(),
                area,
                calculator.quantity,
                D(20),
                calculator.price_per_unit(None),
                D("0.9"),
                calculator.discount,
                D(10),
                calculator.multifile_price(),
                D(0),
                calculator.unit_price_without_discount(None),
                D("1"),
            ]
            txt="\nprice: \t {0} \t {1} \n"
            txt+="area: \t {2} \t {3} \n"
            txt+="quantity: \t {4} \t {5} \n"
            txt+="price per unit: \t {6} \t {7} \n"
            txt+="discount: \t {8} \t {9} \n"
            txt+="multi file: \t {10} \t {11} \n"
            txt+="rpl: \t {12} \t {13} \n"
            raise AssertionError(txt.format(*error))


    def test_calculator(self):
        data={
            "quantity":"20",
            "number_of_files":1,
            "width":0,"height":0}
        qs = OptionChoice.objects.filter(code="big")
        assert(qs.count()==1)
        calculator=OptionsCalculator(self.product,qs,data)
        if not calculator.total_price(self.user)==D(20)*D("0.9")*D("1.2"):
            error=[
                calculator.total_price(self.user),
                D(20)*D("0.9")*D("1.2")
            ]
            raise AssertionError("{0} \n {1}".format(error))



