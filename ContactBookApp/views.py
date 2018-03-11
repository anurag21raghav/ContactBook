from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import ContactValidator, EmailTrie, NameTrie
from .models import Contact

email_trie = EmailTrie()
name_trie = NameTrie()
contacts = Contact.objects.all()
for contact in contacts:
    email_trie.insert(contact.email, contact.name)
    name_trie.insert(contact.name, contact.email)

def paginate(request, data, strength):
    paginator = Paginator(data, strength)
    page = request.GET.get('page')
    try:
    	data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)
    return data.object_list

class SearchAPIView(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        data = request.GET
        key = data.get('key', '').lower()
        data = (email_trie.search(key)) + (name_trie.search(key))
        data = list({v['email']:v for v in data}.values())
        data = paginate(request, data, 10)
        return Response(data=data, status=status.HTTP_200_OK)


class ContactBookAPIView(APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        all_contacts = Contact.objects.all()
        data_list = list()
        for contact in all_contacts:
            data_item = contact.__dict__
            data_item.pop('_state', None)
            data_list.append(data_item)
        data = paginate(request, data_list, 10)
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        data['owner_id'] = self.request.user.pk
        owner_id=self.request.user.pk
        new_contact = ContactValidator(**data)
        new_contact.validate()
        if new_contact.errors:
            return Response(data=new_contact.errors, status=status.HTTP_400_BAD_REQUEST)
        Contact.objects.create(**new_contact.data)
        email = new_contact.data.get('email', '')
        name = new_contact.data.get('name', '')
        email_trie.insert(email, name)
        res = name_trie.search(name)
        if not res:
        	name_trie.insert(name, email)
        else:
        	name_trie.update(name, email)
        return Response(data=new_contact.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
    	data = request.data
    	name = data.get('name', '').lower()
    	email = data.get('email', '').lower()
    	res = email_trie.search(email)
    	if not res:
    		return Response(data={'email': 'No contact associated with provided email address'}, status=status.HTTP_204_NO_CONTENT)
    	contact = Contact.objects.get(email=email)
    	prev_name = contact.name
    	contact.name = name
    	contact.save()
    	email_trie.update(email, name)
    	name_trie.deleteKey(prev_name, email)
    	contact_search = name_trie.search(name)
    	if not contact_search:
    		name_trie.insert(name, email)
    	else:
    		name_trie.update(name, email)
    	return Response(status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        data = request.data
        email = data.get('email', '').lower()
        try:
            print (email, data)
            contact = Contact.objects.get(email=email)
            contact.delete()
        except Contact.DoesNotExist:
            return Response(data={'email': 'This contact is not listed in your Contact Book'}, status=status.HTTP_204_NO_CONTENT)
        contact = email_trie.search(email)
        name = contact[0].get('name', '')
        email_trie.deleteKey(email)
        name_trie.deleteKey(name, email)
        return Response(status=status.HTTP_200_OK)

Search = SearchAPIView.as_view()
ContactBook = ContactBookAPIView.as_view()
