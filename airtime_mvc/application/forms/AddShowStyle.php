<?php

require_once 'customfilters/ImageSize.php';

class Zend_File_Transfer_Adapter_HttpDummy extends Zend_File_Transfer_Adapter_Http
{
    public function isValid($files = null)
    {
        if ($this->_options['ignoreNoFile']) {
            return true;
        }

        return parent::isValid($files);
    }
}

class Application_Form_AddShowStyle extends Zend_Form_SubForm
{

    public function init()
    {
       // Add show background-color input
        $this->addElement('text', 'add_show_background_color', array(
            'label'      => _('Background Colour:'),
            'class'      => 'input_text',
            'filters'    => array('StringTrim')
        ));

        $bg = $this->getElement('add_show_background_color');

        $bg->setDecorators(array(array('ViewScript', array(
            'viewScript' => 'form/add-show-style.phtml',
            'class'      => 'big'
        ))));

        $stringLengthValidator = Application_Form_Helper_ValidationTypes::overrideStringLengthValidator(6, 6);
        $bg->setValidators(array(
            'Hex', $stringLengthValidator
        ));

    // Add show color input
        $this->addElement('text', 'add_show_color', array(
            'label'      => _('Text Colour:'),
            'class'      => 'input_text',
            'filters'    => array('StringTrim')
        ));

        $c = $this->getElement('add_show_color');

        $c->setDecorators(array(array('ViewScript', array(
            'viewScript' => 'form/add-show-style.phtml',
            'class'      => 'big'
        ))));

        $c->setValidators(array(
                'Hex', $stringLengthValidator
        ));

        
        // Show Logo
        $stationLogoUpload = new Zend_Form_Element_File('add_show_logo');
        $stationLogoUpload->setLabel(_('Show Logo:'))
            ->addValidator('Count', false, 1)
            ->addValidator('Extension', false, 'jpg,jpeg,png,gif')
            ->setRequired(false)
            ->setMaxFileSize(5 * 1024 * 1024)
            ->addFilter('ImageSize');
        $stationLogoUpload->setAttrib('accept', 'image/*');
        $stationLogoUpload->setTransferAdapter(new Zend_File_Transfer_Adapter_HttpDummy());
        $this->addElement($stationLogoUpload);

        //Show Logo Preview
        $stationLogoPreview = new Zend_Form_Element_Image('add_show_logo_preview');
        $stationLogoPreview->setLabel(_('Logo Preview:'));
        $stationLogoPreview->getDecorator('Label')->setOption('style', 'display: none;');
        $stationLogoPreview->setAttrib('disabled', 'disabled');
        $stationLogoPreview->setAttrib('src', '');
        $stationLogoPreview->setAttrib('style', 'display:none;');
        $this->addElement($stationLogoPreview);

        //Show Logo Remove Button
        $stationLogoRemove = new Zend_Form_Element_Button('add_show_logo_remove');
        $stationLogoRemove->setLabel(_('Remove'));
        $stationLogoRemove->setAttrib('class', 'btn');
        $stationLogoRemove->setAttrib('style', 'display:none;');
        $this->addElement($stationLogoRemove);        
    }

    public function disable()
    {
        $elements = $this->getElements();
        foreach ($elements as $element) {
            if ($element->getType() != 'Zend_Form_Element_Hidden') {
                $element->setAttrib('disabled','disabled');
            }
        }
    }
}
