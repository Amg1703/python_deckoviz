from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import PDF, Job, Image
from .serializers import (
    PDFSerializer, PDFCreateSerializer, PDFListSerializer,
    JobSerializer, JobCreateSerializer, JobUpdateSerializer,
    ImageSerializer, ImageCreateSerializer
)


class PDFInternalViewSet(viewsets.ModelViewSet):
    """Internal API for PDF operations (no authentication)"""
    
    queryset = PDF.objects.all()
    serializer_class = PDFSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PDFCreateSerializer
        elif self.action == 'list':
            return PDFListSerializer
        return PDFSerializer
    
    def create(self, request, *args, **kwargs):
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Log incoming data for debugging
            logger.info(f"Received data: {request.data.keys()}")
            logger.info(f"Received files: {request.FILES.keys()}")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            # Return full object
            # instance = PDF.objects.get(id=serializer.data['id'])
            # output_serializer = PDFSerializer(instance)
            instance = serializer.instance
            output_serializer = PDFSerializer(instance)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error creating PDF: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='extract-page')
    def extract_page(self, request, pk=None):
        """Extract text from a specific page"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            pdf = self.get_object()
            page_number = request.data.get('page_number')
            
            if not page_number:
                return Response(
                    {"error": "page_number is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                text = pdf.extract_page_text(int(page_number))
                return Response({"text": text, "page_number": page_number})
            except ValueError as e:
                return Response(
                    {"error": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.exception(f"Error extracting page text: {str(e)}")
                return Response(
                    {"error": f"Failed to extract text: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            logger.exception(f"Error in extract_page: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class JobInternalViewSet(viewsets.ModelViewSet):
    """Internal API for Job operations (no authentication)"""
    
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return JobUpdateSerializer
        return JobSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full object
        instance = serializer.instance
        output_serializer = JobSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='by-pdf/(?P<pdf_id>[^/.]+)')
    def by_pdf(self, request, pdf_id=None):
        """Get all jobs for a PDF"""
        jobs = self.queryset.filter(pdf_id=pdf_id).order_by('-created_at')
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)


class ImageInternalViewSet(viewsets.ModelViewSet):
    """Internal API for Image operations (no authentication)"""
    
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ImageCreateSerializer
        return ImageSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full object
        instance = serializer.instance
        output_serializer = ImageSerializer(instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='by-job/(?P<job_id>[^/.]+)')
    def by_job(self, request, job_id=None):
        """Get all images for a job"""
        images = self.queryset.filter(job_id=job_id).order_by('-created_at')
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)
