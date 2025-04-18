library(datasets)
data(mtcars)
head(mtcars,10)
?mtcars
library(ggplot2)
ggplot(aes(x=disp, y=mpg), data=mtcars) +geom_point()+ggtitle("Displacement vs miles per gallon") +labs(x="Displacement", y= "Miles per gallon")
mtcars$vs<-as.factor(mtcars$vs)
ggplot(aes(x = vs, y = mpg, fill = vs), data = mtcars) + geom_boxplot()+theme(legend.position = "bottom")
ggplot(aes(x=wt),data=mtcars) + geom_histogram(binwidth=0.5) 
