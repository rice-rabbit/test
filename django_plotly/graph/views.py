from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
import plotly.express as px
from .bin2real import *
from .forms import *
from .models import *

# Create your views here.
def structure_list(request):
    if request.method == 'POST':
        if 'submit_new' in request.POST:
            response = redirect('field_list')
        elif 'submit_del' in request.POST:
            response = _del_structure(request)
        else:
            response = HttpResponse('Undefined')
    else:
        bs_formset = get_binstructure_formset()
        response = render(request, 'graph/structure.html', {'bs_formset': bs_formset})
    return response

def _del_structure(request):
    bs_formset = get_binstructure_formset(data=request.POST)
    delete_binstructure_formset(bs_formset=bs_formset)
    return HttpResponse('Del')

def field_list(request, bs_id=None):
    if request.method == 'POST':
        if 'submit_add' in request.POST:
            response = _append_field_form(request)
        elif 'submit_delete' in request.POST:
            response = _delete_field_form(request)
        elif 'submit_save' in request.POST:
            response = _save_field_formset(request, bs_id)
        else:
            response = HttpResponse('Undefined')
    else:
        if bs_id is not None: # Field list for the BinStructure(bs_id)
            bs = get_object_or_404(BinStructure, pk=bs_id)
            bs_form = BinStructureForm(instance=bs)
            bf_formset = get_binfield_formset(srctype='bs_id', src=bs_id)
        else: # Empty field list
            bs_form = BinStructureForm()
            bf_formset = get_binfield_formset()
        response = render(request, 'graph/field.html', {'bs_form': bs_form, 'bf_formset': bf_formset})
    return response

def _append_field_form(request):
    bs_form = BinStructureForm(data=request.POST)
    bf_formset = get_binfield_formset(srctype='post', src=request.POST)
    bf_formset = get_binfield_formset(srctype='formset_append', src=bf_formset)
    return render(request, 'graph/field.html', {'bs_form': bs_form, 'bf_formset': bf_formset})

def _delete_field_form(request):
    bs_form = BinStructureForm(data=request.POST)
    bf_formset = get_binfield_formset(srctype='post', src=request.POST)
    bf_formset = get_binfield_formset(srctype='formset_delete', src=bf_formset)
    return render(request, 'graph/field.html', {'bs_form': bs_form, 'bf_formset': bf_formset})

def _save_field_formset(request, bs_id):
    bs_form = BinStructureForm(data=request.POST)
    bf_formset = get_binfield_formset(srctype='post', src=request.POST)
    saved = save_binstructure_binfield_formset(bs_form=bs_form, bs_id=bs_id, bf_formset=bf_formset)
    if saved:
        response = HttpResponse('Saved')
    else:
        response = HttpResponse('Invalid')
    return response

def plot(request):
    if request.method == 'POST':
        sel_bs = SelectBinStructureForm(data=request.POST)
        if sel_bs.is_valid():

            # Make binary structure from the selected BinStructure
            cbs = CustomBinStructure()
            bs_name = sel_bs.cleaned_data['bs']
            bfs = BinField.objects.filter(bs__name=bs_name)
            for bf in bfs:
               cbs.append_field(bf.label, bf.bits) 
            cbs.make_binstructure()

            # Read a sample file
            cbs_dict = cbs.read_bin_to_dict('graph/sample.bin')

            # Plot
            fig = px.scatter(x=cbs_dict['use22bits'], y=cbs_dict['use2bits'])
            plot_div = fig.to_html(full_html=False)
            response = render(request, 'graph/plot.html', {'plot_div': plot_div})
        else:
            response = HttpResponse('post')
    else:
        sel_bs = SelectBinStructureForm()
        response = render(request, 'graph/plot.html', {'sel_bs': sel_bs})
    return response
