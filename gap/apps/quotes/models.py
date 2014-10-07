import datetime
from random import randint

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import transaction

from apps.options.calc import OptionsCalculator, PriceNotAvailable
from apps.options.models import OptionChoice, ArtworkItem
from apps.basket.models import Basket
from apps.globals.models import get_tax_percent
from apps.partner.wrappers import DefaultWrapper

Product = models.get_model('catalogue', 'Product')


class Quote(models.Model):

    caption = models.CharField(max_length=30, default='', blank=True)
    reference_number = models.CharField(max_length=10, unique=True, blank=False)
    user = models.ForeignKey(User, related_name='quotes')
    total_price = models.DecimalField(max_digits=11, decimal_places=3,
                                    validators=[MinValueValidator(0)],
                                    verbose_name='Total quote price',
                                    default=0)
    hash_code = models.CharField(max_length=35, default='', blank=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField(default=datetime.datetime.now()
                                        + datetime.timedelta(days=30))

    def __unicode__(self):
        return '{0} by {1}'.format(self.caption, self.user)

    class Meta:
        unique_together = ('user', 'hash_code')
        ordering = ['-date_added']

    @classmethod
    @transaction.commit_on_success
    def get_or_create_from_basket(cls, user, basket):
        """
            Takes current basket content and saves all information as a quote
            or returns existing saved quote with this content
        """
        lines = basket.all_lines()
        basket_hash = basket.get_hash()
        quote_id = cls.quote_exists(user.id, basket_hash)

        if quote_id:
            is_new = False
            try:
                quote = Quote.objects.get(id=quote_id)
            except Quote.DoesNotExist:
                quote = False
        else:
            quote = cls()
            quote.user_id = user.id
            quote.save()

            total_price = 0
            for line in lines:

                price = cls.get_price(line, user.id)
                total_price += price

                quoteline = QuoteLine(
                    quote=quote,
                    product=line.product,
                    quantity=line.quantity,
                    price_excl_tax=line.unit_price_excl_tax,
                    price_incl_tax=line.unit_price_incl_tax,
                    price=cls.get_price_incl_tax(price),
                    width=line.width,
                    height=line.height,
                    is_dead=line.is_dead
                )
                quoteline.save(force_insert=True)

                option_choices = []
                for option_choice in line.get_option_choices():
                    option_choices.append(option_choice)

                quoteline.choices.add(*option_choices)

            quote.hash_code = basket_hash
            quote.caption = cls.get_caption(lines)
            quote.total_price = cls.get_price_incl_tax(total_price)
            quote.save()
            is_new = True

        return (quote, is_new)

    @staticmethod
    def get_price(line, user_id):
        data = {
            'quantity': line.quantity,
            'number_of_files': line.number_of_files,
            'width': line.width,
            'height': line.height
        }
        calc = OptionsCalculator(line.product, line.choices.all(), data)
        return calc.total_price(User.objects.get(id=user_id))

    @staticmethod
    def get_price_incl_tax(price):
        wr = DefaultWrapper(get_tax_percent())
        return wr.get_total_price_incl_tax(price)

    # TODO
    # def is_valid(self):
    #     calc = OptionsCalculator(self.product)
    #     prices = calc.calculate_costs(
    #         list(self.choices.all()), self.quantity, json.loads(self.choice_data))
    #     try:
    #         prices.get_price_incl_tax(self.quantity, 1, self.user)
    #     except PriceNotAvailable:
    #         return False

    @classmethod
    def get_caption(cls, lines):
        caption = ''  # TODO
        return caption

    @classmethod
    def quote_exists(cls, user_id, basket_hash):
        """
            Check if the quote with the same basket line data
            is already saved.

            This is necessary because when user uses
            'Print Quote', 'Save Quote', 'Email Quote' buttons
            he needs to operate on the same quote all the time.
            'Print Quote' and 'Email Quote' save quote internally
            before printing or sending it.
            If user sends quote first and then decides that he wants a PDF
            - the same quote is retrieved to be rendered as a PDF file
        """
        if basket_hash:
            try:
                quote = Quote.objects.get(hash_code=basket_hash, user_id=user_id)
            except Quote.DoesNotExist:
                pass
            else:
                return quote.id

        return False

    def save(self):

        random_number = randint(1000000000, 9999999999)

        while Quote.objects.filter(reference_number=random_number):
            random_number = randint(1000000000, 9999999999)

        self.reference_number = random_number

        super(Quote, self).save()


class QuoteLine(models.Model):

    quote = models.ForeignKey(Quote)
    product = models.ForeignKey(Product, blank=False)
    quantity = models.PositiveIntegerField(blank=False, default=1)

    choices = models.ManyToManyField(OptionChoice, related_name='choices')

    price_excl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    price_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, null=True)

    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    is_dead = models.BooleanField(blank=True, default=False)


class QuoteLineAttachment(models.Model):
    pass


class QuoteLineAttribute(models.Model):
    pass

