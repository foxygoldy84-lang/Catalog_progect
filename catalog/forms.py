from django import forms

from catalog.models import Product

# Слова, которые запрещено использовать в названии и описании продукта
FORBIDDEN_WORDS = (
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
)

# Максимальный размер загружаемого изображения — 5 МБ
MAX_IMAGE_SIZE = 5 * 1024 * 1024

# Разрешённые форматы изображений: MIME-тип -> человекочитаемое название
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "JPEG",
    "image/png": "PNG",
}


class ProductForm(forms.ModelForm):
    """Форма создания и редактирования продукта."""

    class Meta:
        model = Product
        fields = ("name", "description", "image", "category", "price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Единый стиль для всех полей формы
        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            else:
                widget.attrs["class"] = "form-control"

            if name == "description":
                widget.attrs.setdefault("rows", 3)

            if name == "image":
                widget.attrs["accept"] = "image/jpeg,image/png"
            elif isinstance(
                widget, (forms.TextInput, forms.Textarea, forms.NumberInput)
            ):
                widget.attrs.setdefault("placeholder", field.label)

    @staticmethod
    def _find_forbidden_words(value):
        """Возвращает запрещённые слова, найденные в тексте без учёта регистра."""
        if not value:
            return []
        lowered_value = value.lower()
        return [word for word in FORBIDDEN_WORDS if word in lowered_value]

    def _validate_forbidden_words(self, value, field_name):
        found_words = self._find_forbidden_words(value)
        if found_words:
            words = ", ".join(f"«{word}»" for word in found_words)
            raise forms.ValidationError(
                f"В {field_name} продукта нельзя использовать слова: {words}."
            )
        return value

    def clean_name(self):
        """Проверяет название продукта на запрещённые слова."""
        name = self.cleaned_data["name"]
        return self._validate_forbidden_words(name, "названии")

    def clean_description(self):
        """Проверяет описание продукта на запрещённые слова."""
        description = self.cleaned_data.get("description") or ""
        return self._validate_forbidden_words(description, "описании")

    def clean_price(self):
        """Проверяет, что цена продукта не отрицательная."""
        price = self.cleaned_data["price"]
        if price is not None and price < 0:
            raise forms.ValidationError("Цена продукта не может быть отрицательной.")
        return price

    def clean_image(self):
        """Проверяет формат и размер загружаемого изображения."""
        image = self.cleaned_data.get("image")
        if not image:
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError("Размер изображения не должен превышать 5 МБ.")

        content_type = getattr(image, "content_type", "")
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise forms.ValidationError("Загрузите изображение в формате JPEG или PNG.")

        return image
