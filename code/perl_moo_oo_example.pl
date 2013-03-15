package Shape;

use Moo;

sub draw    {}
sub moveTo  {}
sub rMoveTo {}

1;

package Rectangle;

use Moo;

extends 'Shape';

has x     => ( is => 'ro' );
has y     => ( is => 'ro' );
has width => ( is => 'ro' );
has height=> ( is => 'ro' );

sub draw {
    my $self = shift;
    print "drawing a Rectangle at ($self->{x}, $self->{y}, width $self->{width}, height $self->{height})\n";
}

sub moveTo {
    my ($self, $newX, $newY) = @_;
    # $self->x($newX); 这样使用会报错,因为 x 是 ready-only 的
    $self->{x} = $newX;
    $self->{y} = $newY;
}

sub rMoveTo {
    my ($self, $dx, $dy) = @_;
    $self->{x} += $dx;
    $self->{y} += $dy;
}

1;

package Circle;

use Moo;

extends 'Shape';

has radius => ( is => 'ro' );

sub draw {
    my $self = shift;
    print "drawing a Circle at ($self->{x}, $self->{y}, radius $self->{radius})\n";
}

sub moveTo {
    my ($self, $x, $y) = @_;
    $self->{x} = $x;
    $self->{y} = $y;
}

package main;

my $shape = Rectangle->new({
    x => 1,
    y => 2,
    width => 1,
    height => 2,
});

$shape->moveTo(1,2);
$shape->draw;
$shape->rMoveTo(1,2);
$shape->draw;

my $circle = Circle->new(
    x => 0,
    y => 0,
    radius => 10,
);

$circle->moveTo(2,2);
$circle->draw;
$circle->rMoveTo;
