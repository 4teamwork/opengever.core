/*
Remove links from trix document model to prevent that links can be copy-pasted
into trix even though we have disabled the link buttons.
 */
delete Trix.config.textAttributes.href
