import datetime
from random import randint

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import transaction

from apps.options.calc import OptionsCalculator
from apps.options.models import OptionChoice
from apps.basket.models import Basket

Product = models.get_model('catalogue', 'Product')


class Quote(models.Model):

    caption = models.CharField(max_length=30, default='', blank=True)
    reference_number = models.CharField(max_length=10, unique=True, blank=False)
    user = models.ForeignKey(User, related_name='quotes')
    total_price = models.DecimalField(max_digits=11, decimal_places=3,
                                    validators=[MinValueValidator(0)],
                                    verbose_name='Total quote price',
                                    default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_expired = models.DateTimeField(default=datetime.datetime.now()
                                        + datetime.timedelta(days=30))

    def __unicode__(self):
        return '{0} by {1}'.format(self.caption, self.user)

    class Meta:
        ordering = ['-date_added']

    @classmethod
    @transaction.commit_on_success
    def save_quote(cls, user_id):
        """
            Takes current basket content and saves all information as a quote
        """
        lines = cls.get_basket_lines(user_id)

        if not cls.quote_exists(user_id, lines):

            quote = cls()
            quote.user_id = user_id
            quote.save()

            total_price = 0
            for line in lines:

                price = cls.get_price(line, user_id)
                total_price += price

                quoteline = QuoteLine(
                    quote=quote,
                    product=line.product,
                    quantity=line.quantity,
                    price_excl_tax=0,
                    price_incl_tax=price,
                    width=0,
                    height=0,
                    is_dead=line.is_dead
                )
                quoteline.save(force_insert=True)

                option_choices = []
                for option_choice in line.get_option_choices():
                    option_choices.append(option_choice)

                quoteline.choices.add(*option_choices)

            quote.total_price = total_price
            quote.save()

            return quote.id

        else:
            return False

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
    def get_basket_lines(user_id):
        try:
            basket = Basket.objects.get(owner_id=user_id)
        except Basket.DoesNotExist:
            return False
        return basket.all_lines()  # TODO: handle is_dead flag

    @classmethod
    def quote_exists(cls, user_id, lines):
        """
            Check if the quote with the same basket line data
            is already saved.
        """

        return False # for now, until further development milestones and querybuilder behavior become clear

        if lines:

            # TODO - possible optimization?
            line_choices = dict()
            for line in lines:
                line_choices[line.id] = dict(
                    (choice.option, choice.code) for choice in line.choices.all())

            existing_user_quotes = Quote.objects.filter(user_id=user_id)

            saved_quote_id = False
            for quote in existing_user_quotes:
                if len(lines) != quote.quoteline_set.count():
                    continue
                else:
                    quote_choices = dict()
                    for quoteline in quote.quoteline_set.all():
                        quote_choices = dict(
                            (choice.option, choice.code) for choice in quoteline.choices.all())

                        for line_choice in line_choices:
                            shared_choices = set(line_choices.items()) & set(quote_choices.items())
                            if len(shared_choices) == len(lines):
                                saved_quote_id = quote.id

                    if saved_quote_id:
                        break

            return saved_quote_id

        return False

    def save(self):

        random_number = randint(1000000000, 9999999999)

        while Quote.objects.filter(reference_number=random_number):
            random_number = randint(1000000000, 9999999999)

        self.reference_number = random_number

        super(Quote, self).save()

    # TODO: check when price can be invalid
    # def is_valid(self):
    #     calc = OptionsCalculator(self.product)
    #     prices = calc.calculate_costs(
    #         list(self.choices.all()), self.quantity, json.loads(self.choice_data))
    #     try:
    #         prices.get_price_incl_tax(self.quantity, 1, self.user)
    #     except PriceNotAvailable:
    #         return False

    #     return True


class QuoteLine(models.Model):

    quote = models.ForeignKey(Quote)
    product = models.ForeignKey(Product, blank=False)
    quantity = models.PositiveIntegerField(blank=False, default=1)

    choices = models.ManyToManyField(OptionChoice, related_name='choices')

    price_excl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True)
    price_incl_tax = models.DecimalField(decimal_places=2, max_digits=12, null=True)

    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)

    is_dead = models.BooleanField(blank=True, default=False)
