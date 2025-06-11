from rest_framework.views import APIView
from django.http import JsonResponse
from django.db import transaction
from http import HTTPStatus
import json

from .models import Invoice
from rental.models import Rental
from payment.models import Payment
from .serializers import InvoiceSerializer, PaymentSerializer
from .forms import InvoiceCreateForm, InvoiceStatusUpdateForm
from utilities.decorators import authenticate_user

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from utilities.utilities import sendMail


class InvoiceRC(APIView):

    @authenticate_user(required_permission='invoice.view_invoice')
    def get(self, request):
        try:
            invoices = Invoice.objects.select_related('rental__customer').filter(active=True)
            serializer = InvoiceSerializer(invoices, many=True)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Ocurrió un error: {str(e)}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    @authenticate_user(required_permission='invoice.add_invoice')
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id if request.user.is_authenticated else None
        
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Cuerpo de la solicitud inválido."}, status=HTTPStatus.BAD_REQUEST)

        form = InvoiceCreateForm(payload)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            new_invoice = Invoice.objects.create(
                rental_id=cleaned_data['rental_id'],
                total_amount=cleaned_data['total_amount'],
                reference=cleaned_data['reference_detail'],
                status=cleaned_data['status'],
                created_by=user_id,
                modified_by=user_id
            )

            message = "Factura creada exitosamente."

            if new_invoice.status == 'Emitida':
                try:
                    customer = new_invoice.rental.customer
                    if customer.email:
                        pdf_data = generate_invoice_pdf(new_invoice)
                        pdf_filename = f"Factura-{new_invoice.invoice_number}.pdf"
                        html_body = f"<p>Hola {customer.__str__()},</p><p>Adjuntamos tu nueva factura N° {new_invoice.invoice_number}.</p>"
                        
                        sendMail(
                            html_content=html_body,
                            subject=f"Nueva Factura - N° {new_invoice.invoice_number}",
                            recipient_email=customer.email,
                            attachment_data=pdf_data,
                            attachment_filename=pdf_filename
                        )
                        message += f" La factura ha sido enviada a {customer.email}."
                    else:
                        message += " No se pudo enviar el correo (cliente sin email)."
                except Exception as e:
                    print(f"Error al enviar correo de creación para factura {new_invoice.id}: {e}")
                    message += " Hubo un error al intentar enviar el correo."

            serializer = InvoiceSerializer(new_invoice)
            return JsonResponse({
                "status": "success", "message": message, "data": serializer.data
            }, status=HTTPStatus.CREATED)
        else:
            return JsonResponse({
                "status": "error", "message": "Datos inválidos.", "errors": form.errors.get_json_data()
            }, status=HTTPStatus.BAD_REQUEST)

class InvoiceRU(APIView):

    @authenticate_user(required_permission='invoice.view_invoice')
    def get(self, request, id):
        try:
            invoice = Invoice.objects.select_related('rental__customer').get(pk=id, active=True)
            serializer = InvoiceSerializer(invoice)
            return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
        except Invoice.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Factura no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)

    @authenticate_user(required_permission='invoice.change_invoice')
    @transaction.atomic
    def put(self, request, id):
        user_id = request.user.id if request.user.is_authenticated else None
        try:
            invoice = Invoice.objects.select_related('rental__customer').get(pk=id, active=True)
        except Invoice.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Factura no encontrada o inactiva."}, status=HTTPStatus.NOT_FOUND)

        if invoice.status == 'Anulada':
            return JsonResponse({
                "status": "error", "message": "Una factura anulada no puede ser modificada."
            }, status=HTTPStatus.BAD_REQUEST)

        payload = json.loads(request.body)
        form = InvoiceStatusUpdateForm(payload, instance=invoice)

        if form.is_valid():
            if form.has_changed():
                updated_invoice = form.save(commit=False)
                updated_invoice.modified_by = user_id
                updated_invoice.save()
                
                message = "Factura actualizada exitosamente."
                
                if 'status' in form.changed_data and updated_invoice.status == 'Anulada':
                    try:
                        customer = updated_invoice.rental.customer
                        if customer.email:
                            html_body = f"""
                                <p>Hola {customer.__str__()},</p>
                                <p>Te informamos que la factura con número <strong>{updated_invoice.invoice_number}</strong> 
                                emitida el {updated_invoice.issue_date.strftime('%d-%m-%Y')} ha sido <strong>anulada</strong>.</p>
                            """
                            sendMail(
                                html_content=html_body,
                                subject=f"Anulación de Factura N° {updated_invoice.invoice_number}",
                                recipient_email=customer.email
                            )
                            message += " Se ha notificado la anulación al cliente."
                    except Exception as e:
                        print(f"Error al enviar correo de anulación para factura {updated_invoice.id}: {e}")
                        message += " Hubo un error al notificar la anulación."
                
                return JsonResponse({"status": "success", "message": message}, status=HTTPStatus.OK)
            else:
                return JsonResponse({"status": "info", "message": "No se detectaron cambios en los datos."}, status=HTTPStatus.OK)
        else:
            return JsonResponse({
                "status": "error", "message": "Datos inválidos.", "errors": form.errors.get_json_data()
            }, status=HTTPStatus.BAD_REQUEST)


class AutomaticInvoice(APIView):

    @authenticate_user(required_permission='invoice.view_invoice')
    def get(self, request, id):
        try:
            rental = Rental.objects.select_related('customer').get(pk=id)
        except Rental.DoesNotExist:
            return JsonResponse({"status": "error", "message": f"Alquiler #{id} no encontrado."}, status=HTTPStatus.NOT_FOUND)

        if rental.status != 'Finalizado':
            return JsonResponse({"status": "error", "message": "Esta función solo aplica a alquileres finalizados."}, status=HTTPStatus.BAD_REQUEST)

        conceptos_facturables = ['Anticipo', 'Pago Final', 'Cargo Adicional', 'Cargo por Retraso']

        pagos_sugeridos = Payment.objects.filter(rental=rental, concept__in=conceptos_facturables, active=True)

        if rental.customer.customer_type == 'Extranjero':
            deposito_a_excluir = Payment.objects.filter(
                rental=rental, 
                amount=100.00, 
                concept='Anticipo',
                active=True
            ).order_by('payment_date').first()

            if deposito_a_excluir:
                pagos_sugeridos = pagos_sugeridos.exclude(pk=deposito_a_excluir.pk)

        serializer = PaymentSerializer(pagos_sugeridos, many=True)
        return JsonResponse({
            "rental_id": rental.id,
            "customer_info": {
                "name": rental.customer.__str__(),
                "type": rental.customer.customer_type
            },
            "suggested_payments": serializer.data
        }, status=HTTPStatus.OK)

class PaymentsRental(APIView):

    @authenticate_user(required_permission='payment.view_payment')
    def get(self, request, id):

        if not Rental.objects.filter(pk=id).exists():
            return JsonResponse({"status": "error", "message": f"Alquiler #{id} no encontrado."}, status=HTTPStatus.NOT_FOUND)
        
        payments = Payment.objects.filter(rental_id=id, active=True).order_by('payment_date')
        serializer = PaymentSerializer(payments, many=True)
        return JsonResponse({"data": serializer.data}, status=HTTPStatus.OK)
    

class IssueInvoice(APIView):
    @authenticate_user(required_permission='invoice.change_invoice')
    def post(self, request, id):
        try:
            invoice = Invoice.objects.select_related('rental__customer').get(pk=id)
        except Invoice.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Factura no encontrada."}, status=HTTPStatus.NOT_FOUND)

        customer = invoice.rental.customer
        if not customer.email:
            return JsonResponse({"status": "error", "message": "El cliente no tiene un correo electrónico registrado."}, status=HTTPStatus.BAD_REQUEST)

        try:
            pdf_data = generate_invoice_pdf(invoice)
            pdf_filename = f"Factura-{invoice.invoice_number}.pdf"

            html_body = f"<p>Hola {customer.__str__()},</p><p>Adjuntamos tu factura N° {invoice.invoice_number}.</p><p>Gracias por tu preferencia.</p>"
            
            sendMail(
                html_content=html_body,
                subject=f"Factura de Tu Empresa - N° {invoice.invoice_number}",
                recipient_email=customer.email,
                attachment_data=pdf_data,
                attachment_filename=pdf_filename
            )

            return JsonResponse({"status": "success", "message": f"Factura enviada exitosamente a {customer.email}."}, status=HTTPStatus.OK)

        except Exception as e:
            print(f"Error en el proceso de emisión de factura {id}: {e}")
            return JsonResponse({"status": "error", "message": f"No se pudo enviar la factura. Error: {e}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)


def generate_invoice_pdf(invoice):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(0.75 * inch, height - 1 * inch, "FACTURA")
    p.setFont("Helvetica", 10)
    p.drawString(0.75 * inch, height - 1.25 * inch, "AutoRent León")
    p.drawString(0.75 * inch, height - 1.40 * inch, "San Miguel Centro")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(4.5 * inch, height - 1 * inch, f"Factura N°: {invoice.invoice_number}")
    p.setFont("Helvetica", 10)
    p.drawString(4.5 * inch, height - 1.25 * inch, f"Fecha de Emisión: {invoice.issue_date.strftime('%d-%m-%Y')}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.75 * inch, height - 2.2 * inch, "Facturar a:")
    p.setFont("Helvetica", 10)
    p.drawString(0.75 * inch, height - 2.4 * inch, f"Cliente: {invoice.rental.customer.__str__()}")
    p.drawString(0.75 * inch, height - 2.55 * inch, f"Email: {invoice.rental.customer.email}")

    p.line(0.75 * inch, height - 3 * inch, width - 0.75 * inch, height - 3 * inch)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(0.75 * inch, height - 3.3 * inch, "Descripción")
    
    p.setFont("Helvetica", 10)
    text_object = p.beginText(0.75 * inch, height - 3.5 * inch)
    for line in invoice.reference.split('\n'):
        text_object.textLine(line)
    p.drawText(text_object)

    p.setFont("Helvetica-Bold", 14)
    total_text = f"TOTAL: ${invoice.total_amount:,.2f}"
    p.drawRightString(width - 0.75 * inch, 1.5 * inch, total_text)

    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()