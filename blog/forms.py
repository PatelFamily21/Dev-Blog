from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Post, Comment, Tag

# Shared inline style that forces correct colours regardless of browser defaults
INPUT_STYLE = (
    "width:100%;"
    "background:#1c2128 !important;"
    "border:1px solid #30363d;"
    "border-radius:10px;"
    "padding:0.65rem 1rem;"
    "font-size:0.9rem;"
    "color:#e6edf3 !important;"
    "outline:none;"
    "transition:border-color 0.2s,box-shadow 0.2s;"
    "font-family:'Plus Jakarta Sans',sans-serif;"
)

INPUT_FOCUS_JS = (
    "this.style.borderColor='#388bfd';"
    "this.style.boxShadow='0 0 0 3px rgba(56,139,253,0.15)'"
)
INPUT_BLUR_JS = (
    "this.style.borderColor='#30363d';"
    "this.style.boxShadow='none'"
)


def input_attrs(placeholder="", extra=""):
    return {
        "style": INPUT_STYLE + extra,
        "onfocus": INPUT_FOCUS_JS,
        "onblur": INPUT_BLUR_JS,
        "placeholder": placeholder,
    }


def textarea_attrs(placeholder="", rows=4, extra=""):
    return {
        "style": INPUT_STYLE + f"resize:vertical;height:auto;" + extra,
        "rows": rows,
        "onfocus": INPUT_FOCUS_JS,
        "onblur": INPUT_BLUR_JS,
        "placeholder": placeholder,
    }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "username": "Choose a username",
            "first_name": "First name",
            "last_name": "Last name",
            "email": "your@email.com",
            "password1": "Create a strong password",
            "password2": "Repeat your password",
        }
        for name, field in self.fields.items():
            ph = placeholders.get(name, "")
            if hasattr(field.widget, "input_type") and field.widget.input_type == "password":
                field.widget.attrs.update({
                    "style": INPUT_STYLE + "padding-right:3rem;",
                    "onfocus": INPUT_FOCUS_JS,
                    "onblur": INPUT_BLUR_JS,
                    "placeholder": ph,
                })
            else:
                field.widget.attrs.update(input_attrs(ph))


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(input_attrs("Username"))
        self.fields["password"].widget.attrs.update({
            "style": INPUT_STYLE + "padding-right:3rem;",
            "onfocus": INPUT_FOCUS_JS,
            "onblur": INPUT_BLUR_JS,
            "placeholder": "Password",
        })


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ("avatar", "bio", "website", "twitter", "github", "location")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

        for name, field in self.fields.items():
            if name == "avatar":
                field.widget.attrs.update({"class": "hidden", "id": "avatar-upload"})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update(textarea_attrs("Tell the world about yourself…", rows=3))
            else:
                field.widget.attrs.update(input_attrs())


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            **input_attrs("Add tags separated by commas  e.g. python, django, web"),
        }),
    )

    class Meta:
        model = Post
        fields = ("title", "cover_image", "body", "excerpt", "status")
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Post title…",
                "style": (
                    "width:100%; background:transparent !important; border:0;"
                    "border-bottom:2px solid #30363d; border-radius:0; padding:0.75rem 0;"
                    "font-size:1.875rem; font-weight:700; color:#e6edf3 !important;"
                    "outline:none; font-family:'Plus Jakarta Sans',sans-serif;"
                    "transition:border-color 0.2s;"
                ),
                "onfocus": "this.style.borderBottomColor='#388bfd'",
                "onblur": "this.style.borderBottomColor='#30363d'",
            }),
            "body": forms.Textarea(attrs={
                "placeholder": "Write your article here… Markdown is supported",
                "rows": 22,
                "style": (
                    INPUT_STYLE
                    + "resize:none; font-family:'JetBrains Mono',Consolas,monospace;"
                    + "font-size:0.875rem; line-height:1.75;"
                ),
                "onfocus": INPUT_FOCUS_JS,
                "onblur": INPUT_BLUR_JS,
            }),
            "excerpt": forms.Textarea(attrs={
                "placeholder": "Short description (auto-generated if left empty)…",
                "rows": 3,
                **textarea_attrs(),
            }),
            "status": forms.Select(attrs={
                "style": (
                    "background:#1c2128 !important; border:1px solid #30363d; border-radius:10px;"
                    "padding:0.5rem 1rem; color:#e6edf3 !important; outline:none;"
                    "font-family:'Plus Jakarta Sans',sans-serif; font-size:0.85rem;"
                    "transition:border-color 0.2s;"
                ),
                "onfocus": INPUT_FOCUS_JS,
                "onblur": INPUT_BLUR_JS,
            }),
            "cover_image": forms.FileInput(attrs={
                "class": "hidden",
                "id": "cover-image-upload",
                "accept": "image/*",
            }),
        }

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            tags_input = self.cleaned_data.get("tags_input", "")
            if tags_input:
                post.tags.clear()
                from django.utils.text import slugify
                for tag_name in [t.strip().lower() for t in tags_input.split(",") if t.strip()]:
                    tag, _ = Tag.objects.get_or_create(
                        slug=slugify(tag_name), defaults={"name": tag_name}
                    )
                    post.tags.add(tag)
        return post


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(attrs={
                "placeholder": "Share your thoughts…",
                "rows": 4,
                "style": INPUT_STYLE + "resize:none;",
                "onfocus": INPUT_FOCUS_JS,
                "onblur": INPUT_BLUR_JS,
            }),
        }